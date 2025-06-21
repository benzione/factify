import os
import sys
from pathlib import Path

# Add the parent directory to the Python path so imports work correctly
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

from flask import request
from flask_restful import Resource
from typing import Dict, Any, List
from core.document_processor import DocumentProcessor
from core.models import DocumentResult, ApiErrorResponse, ActionableItem
from utils.logger import setup_logging
from utils.exceptions import DocumentNotFoundError, InvalidInputError, DocumentProcessingError, LLMAPIError
from pydantic import ValidationError

logger = setup_logging(__name__)

class DocumentAnalyze(Resource):
    """
    API endpoint for processing and analyzing a new document.
    Endpoint: POST /documents/analyze
    """
    def __init__(self, **kwargs):
        self.document_processor: DocumentProcessor = kwargs['document_processor']

    def post(self):
        logger.info("Received POST request to /documents/analyze")
        
        # Check if a file was uploaded
        if 'file' not in request.files:
            raise InvalidInputError("No file uploaded. Please include a file in the 'file' field of the multipart/form-data request.")
        
        uploaded_file = request.files['file']
        
        # Check if a file was actually selected
        if uploaded_file.filename == '':
            raise InvalidInputError("No file selected for upload.")
        
        # Validate file type (optional - you can add more validation here)
        if not uploaded_file.filename.lower().endswith('.pdf'):
            raise InvalidInputError("Only PDF files are supported.")
        
        # Create a temporary file to store the uploaded content
        import tempfile
        import uuid
        
        # Generate a unique temporary filename to avoid conflicts
        temp_file_id = str(uuid.uuid4())
        temp_filename = f"{temp_file_id}_{uploaded_file.filename}"
        temp_file_path = os.path.join(tempfile.gettempdir(), temp_filename)
        
        try:
            # Save the uploaded file to temporary location
            uploaded_file.save(temp_file_path)
            logger.info(f"Received file '{uploaded_file.filename}', temporarily saved to {temp_file_path}")
            
            # Process the temporary file
            processed_data = self.document_processor.process_document(temp_file_path)
            
            # Remove the temporary file
            os.remove(temp_file_path)
            logger.info(f"Removed temporary file: {temp_file_path}")

            # Validate output using Pydantic model (optional, as processor already returns dict from model)
            # DocumentResult(**processed_data)

            logger.info(f"Document {uploaded_file.filename} processed successfully. ID: {processed_data['document_id']}")
            return processed_data, 200 # Return 200 OK for successful processing
            
        except ValidationError as e:
            # Ensure temporary file is cleaned up
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    logger.info(f"Cleaned up temporary file after validation error: {temp_file_path}")
                except:
                    logger.warning(f"Failed to clean up temporary file: {temp_file_path}")
            
            # This catches validation errors if the processor's output doesn't conform to DocumentResult
            logger.error(f"Pydantic validation error after processing: {e.errors()}", exc_info=True)
            raise DocumentProcessingError(
                "Processed data failed validation.",
                details={"validation_errors": e.errors()}
            )
        except DocumentProcessingError as e:
            # Ensure temporary file is cleaned up
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    logger.info(f"Cleaned up temporary file after processing error: {temp_file_path}")
                except:
                    logger.warning(f"Failed to clean up temporary file: {temp_file_path}")
            
            logger.error(f"Document processing failed: {e.message}")
            raise # Re-raise for centralized error handling
        except LLMAPIError as e:
            # Ensure temporary file is cleaned up
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    logger.info(f"Cleaned up temporary file after LLM error: {temp_file_path}")
                except:
                    logger.warning(f"Failed to clean up temporary file: {temp_file_path}")
            
            logger.error(f"LLM API error during document analysis: {e.message}")
            raise
        except Exception as e:
            # Ensure temporary file is cleaned up even if processing fails
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    logger.info(f"Cleaned up temporary file after unexpected error: {temp_file_path}")
                except:
                    logger.warning(f"Failed to clean up temporary file: {temp_file_path}")
            
            logger.error(f"An unexpected error occurred during document analysis: {e}", exc_info=True)
            raise DocumentProcessingError(f"An unexpected server error occurred: {e}")

class DocumentDetail(Resource):
    """
    API endpoint for retrieving a specific document and its metadata.
    Endpoint: GET /documents/{id}
    """
    def __init__(self, **kwargs):
        self.document_processor: DocumentProcessor = kwargs['document_processor']

    def get(self, document_id: str):
        logger.info(f"Received GET request for /documents/{document_id}")
        document_data = self.document_processor.get_document_metadata(document_id)
        if document_data:
            logger.info(f"Successfully retrieved metadata for document ID: {document_id}")
            return document_data, 200
        else:
            logger.warning(f"Document ID not found: {document_id}")
            raise DocumentNotFoundError(document_id=document_id)

class DocumentActions(Resource):
    """
    API endpoint for retrieving actionable items for a specific document.
    Endpoint: GET /documents/{id}/actions
    """
    def __init__(self, **kwargs):
        self.document_processor: DocumentProcessor = kwargs['document_processor']

    def get(self, document_id: str):
        logger.info(f"Received GET request for /documents/{document_id}/actions with query params: {request.args}")
        status = request.args.get('status')
        deadline = request.args.get('deadline')
        priority = request.args.get('priority')

        # First, check if the document exists
        if document_id not in self.document_processor.processed_documents:
            logger.warning(f"Document ID not found for actions request: {document_id}")
            raise DocumentNotFoundError(document_id=document_id)

        actionable_items = self.document_processor.get_actionable_items(
            document_id=document_id,
            status=status,
            deadline=deadline,
            priority=priority
        )
        
        # Validate each item using Pydantic model
        try:
            validated_items = [ActionableItem(**item).dict() for item in actionable_items]
        except ValidationError as e:
            logger.error(f"Validation error for actionable items for doc {document_id}: {e.errors()}", exc_info=True)
            raise DocumentProcessingError(f"Failed to validate actionable items: {e}")

        logger.info(f"Returning {len(validated_items)} actionable items for document {document_id}.")
        return validated_items, 200

def initialize_routes(api, document_processor_instance: DocumentProcessor):
    """Initializes and adds all API routes to the Flask-RESTful API."""
    api.add_resource(
        DocumentAnalyze,
        '/documents/analyze',
        resource_class_kwargs={'document_processor': document_processor_instance}
    )
    api.add_resource(
        DocumentDetail,
        '/documents/<string:document_id>',
        resource_class_kwargs={'document_processor': document_processor_instance}
    )
    api.add_resource(
        DocumentActions,
        '/documents/<string:document_id>/actions',
        resource_class_kwargs={'document_processor': document_processor_instance}
    )
    logger.info("API routes initialized.") 