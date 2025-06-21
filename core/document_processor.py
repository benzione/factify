import os
import pypdf
import json
import uuid
from typing import Dict, Any, List, Optional
from config.settings import DOCUMENT_TYPES
from core.llm_interface import LLMInterface
from core.models import DocumentResult, DocumentClassification, DocumentMetadata, ActionableItem
from utils.logger import setup_logging
from utils.exceptions import DocumentProcessingError, LLMAPIError, InvalidInputError

logger = setup_logging(__name__)

class DocumentProcessor:
    """
    Facade class for processing documents, orchestrating PDF extraction,
    LLM classification, and metadata extraction.
    """
    def __init__(self):
        self.llm_interface = LLMInterface()
        self.processed_documents: Dict[str, DocumentResult] = {} # In-memory storage for processed documents

    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extracts text content from a PDF file."""
        text = ""
        try:
            with open(pdf_path, 'rb') as f:
                reader = pypdf.PdfReader(f)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text += page.extract_text() or ""
            if not text.strip():
                raise DocumentProcessingError(f"Could not extract any text from PDF: {os.path.basename(pdf_path)}")
            logger.info(f"Successfully extracted text from {os.path.basename(pdf_path)}")
            return text
        except FileNotFoundError:
            raise DocumentProcessingError(f"PDF file not found: {pdf_path}")
        except pypdf.errors.PdfReadError as e:
            raise DocumentProcessingError(f"Failed to read PDF file {os.path.basename(pdf_path)}: {e}")
        except Exception as e:
            raise DocumentProcessingError(f"An unexpected error occurred during text extraction from {os.path.basename(pdf_path)}: {e}", details={"file_path": pdf_path})

    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        Processes a single document: extracts text, classifies, and extracts metadata.
        Returns the structured document result as a dictionary.
        """
        filename = os.path.basename(file_path)
        document_id = str(uuid.uuid4())
        text_content = ""
        classification_data = None
        extracted_metadata = {}
        processing_status = "success"
        error_message = None

        try:
            text_content = self._extract_text_from_pdf(file_path)

            # 1. Document Type Classification
            classification_data = self.llm_interface.classify_document(text_content, DOCUMENT_TYPES)
            doc_type = classification_data.get("type")
            classification_confidence = classification_data.get("confidence")

            # Get metadata fields for the classified document type
            fields_to_extract = DOCUMENT_TYPES.get(doc_type, {}).get("metadata_fields", [])

            # 2. Semantic Metadata Extraction (if fields are defined)
            if fields_to_extract:
                if doc_type == "other":
                    # Use dynamic metadata extraction for "other" documents
                    extracted_metadata = self.llm_interface.extract_dynamic_metadata_for_other(text_content)
                else:
                    # Use standard metadata extraction for specific document types
                    extracted_metadata = self.llm_interface.extract_metadata(text_content, doc_type, fields_to_extract)
                # Filter out None values for cleaner output if preferred, or keep them for explicit missing fields
                # extracted_metadata = {k: v for k, v in extracted_metadata.items() if v is not None}
            else:
                logger.info(f"No specific metadata fields defined for document type: {doc_type}. Skipping metadata extraction.")
                extracted_metadata = {}


        except DocumentProcessingError as e:
            processing_status = "failed"
            error_message = str(e)
            logger.error(f"Document processing failed for {filename}: {e}")
        except LLMAPIError as e:
            processing_status = "failed"
            error_message = f"LLM API error during processing: {e.message}"
            logger.error(f"LLM API error for {filename}: {e.message}", exc_info=True)
        except Exception as e:
            processing_status = "failed"
            error_message = f"An unexpected error occurred: {e}"
            logger.error(f"Unexpected error for {filename}: {e}", exc_info=True)

        # Construct DocumentResult model
        doc_result = DocumentResult(
            document_id=document_id,
            filename=filename,
            classification=DocumentClassification(
                type=classification_data.get("type", "unknown") if classification_data else "unknown",
                confidence=classification_data.get("confidence", 0.0) if classification_data else 0.0
            ),
            metadata=extracted_metadata,
            processing_status=processing_status,
            error_message=error_message
        )

        # Store in-memory
        self.processed_documents[document_id] = doc_result
        return doc_result.dict() # Return as dictionary for API consistency

    def get_document_metadata(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves processed document metadata by ID."""
        doc_result = self.processed_documents.get(document_id)
        if doc_result:
            # Add semantic descriptions to the metadata fields for AI agents
            doc_type = doc_result.classification.type
            semantic_descriptions = DOCUMENT_TYPES.get(doc_type, {}).get("semantic_description", {})
            
            # Create a copy of metadata to add descriptions
            metadata_with_descriptions = {}
            for field, value in doc_result.metadata.items():
                metadata_with_descriptions[field] = {
                    "value": value,
                    "description": semantic_descriptions.get(field, "No specific semantic description available for this field.")
                }
            
            # Create a new dict for the response to include descriptions
            response_data = doc_result.dict()
            response_data["metadata"] = metadata_with_descriptions
            return response_data
        return None

    def get_actionable_items(self, document_id: str, status: Optional[str] = None, deadline: Optional[str] = None, priority: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Extracts and filters actionable items from a processed document.
        This is a simplified example; a real implementation would use LLM for extraction.
        """
        doc_result = self.processed_documents.get(document_id)
        if not doc_result:
            return [] # Or raise DocumentNotFoundError

        actions: List[ActionableItem] = []
        
        # --- Simplified Actionable Item Generation (Placeholder) ---
        # In a real system, you would call the LLM to identify actionable items
        # based on the document's content and metadata.
        # Example: LLM prompt: "Identify any actionable items, deadlines, or tasks from this document."

        # For demonstration, let's create some dummy actions based on invoice/contract examples
        if doc_result.classification.type == "invoice":
            amount = doc_result.metadata.get("amount", {}).get("value") if isinstance(doc_result.metadata.get("amount"), dict) else doc_result.metadata.get("amount")
            due_date = doc_result.metadata.get("due_date", {}).get("value") if isinstance(doc_result.metadata.get("due_date"), dict) else doc_result.metadata.get("due_date")
            vendor = doc_result.metadata.get("vendor", {}).get("value") if isinstance(doc_result.metadata.get("vendor"), dict) else doc_result.metadata.get("vendor")

            if amount and due_date:
                actions.append(ActionableItem(
                    description=f"Pay invoice for {amount} from {vendor or 'unknown vendor'}.",
                    status="pending",
                    deadline=due_date,
                    priority="high",
                    source_field="amount, due_date"
                ))
            if doc_result.metadata.get("line_items"):
                for item in doc_result.metadata["line_items"]:
                    if isinstance(item, dict) and item.get("description"):
                        actions.append(ActionableItem(
                            description=f"Review line item: {item['description']}",
                            status="pending",
                            priority="medium",
                            source_field="line_items"
                        ))

        elif doc_result.classification.type == "contract":
            effective_date = doc_result.metadata.get("effective_date", {}).get("value") if isinstance(doc_result.metadata.get("effective_date"), dict) else doc_result.metadata.get("effective_date")
            termination_date = doc_result.metadata.get("termination_date", {}).get("value") if isinstance(doc_result.metadata.get("termination_date"), dict) else doc_result.metadata.get("termination_date")

            if effective_date:
                actions.append(ActionableItem(
                    description=f"Acknowledge contract effective on {effective_date}.",
                    status="completed", # assuming acknowledgment is prompt
                    priority="low",
                    source_field="effective_date"
                ))
            if termination_date:
                actions.append(ActionableItem(
                    description=f"Review contract for termination on {termination_date}.",
                    status="pending",
                    deadline=termination_date,
                    priority="high",
                    source_field="termination_date"
                ))
            
            if doc_result.metadata.get("key_terms"):
                for term in doc_result.metadata["key_terms"]:
                    if isinstance(term, str) and len(term) > 10: # Simple heuristic for a "meaningful" term
                         actions.append(ActionableItem(
                            description=f"Understand contract term: {term[:50]}...",
                            status="pending",
                            priority="medium",
                            source_field="key_terms"
                        ))

        elif doc_result.classification.type == "other":
            # Handle actionable items for generic "other" documents
            document_title = doc_result.metadata.get("document_title", {}).get("value") if isinstance(doc_result.metadata.get("document_title"), dict) else doc_result.metadata.get("document_title")
            author = doc_result.metadata.get("author", {}).get("value") if isinstance(doc_result.metadata.get("author"), dict) else doc_result.metadata.get("author")
            subject = doc_result.metadata.get("subject", {}).get("value") if isinstance(doc_result.metadata.get("subject"), dict) else doc_result.metadata.get("subject")
            key_points = doc_result.metadata.get("key_points", {}).get("value") if isinstance(doc_result.metadata.get("key_points"), dict) else doc_result.metadata.get("key_points")
            document_purpose = doc_result.metadata.get("document_purpose", {}).get("value") if isinstance(doc_result.metadata.get("document_purpose"), dict) else doc_result.metadata.get("document_purpose")

            # Create a general review action for the document
            if document_title or subject:
                title_or_subject = document_title or subject or "this document"
                actions.append(ActionableItem(
                    description=f"Review and process document: {title_or_subject}",
                    status="pending",
                    priority="medium",
                    source_field="document_title, subject"
                ))

            # Add action based on document purpose if available
            if document_purpose:
                actions.append(ActionableItem(
                    description=f"Address document purpose: {document_purpose[:100]}{'...' if len(document_purpose) > 100 else ''}",
                    status="pending",
                    priority="medium",
                    source_field="document_purpose"
                ))

            # Add actions for key points if available
            if key_points and isinstance(key_points, str):
                actions.append(ActionableItem(
                    description=f"Review key points: {key_points[:100]}{'...' if len(key_points) > 100 else ''}",
                    status="pending",
                    priority="medium",
                    source_field="key_points"
                ))
            elif key_points and isinstance(key_points, list):
                for i, point in enumerate(key_points[:3]):  # Limit to first 3 points
                    if isinstance(point, str) and len(point.strip()) > 5:
                        actions.append(ActionableItem(
                            description=f"Consider key point {i+1}: {point[:80]}{'...' if len(point) > 80 else ''}",
                            status="pending",
                            priority="low",
                            source_field="key_points"
                        ))

            # Add follow-up action if author is identified
            if author:
                actions.append(ActionableItem(
                    description=f"Follow up with document author: {author}",
                    status="pending",
                    priority="low",
                    source_field="author"
                ))

        filtered_actions = []
        for action in actions:
            match = True
            if status and action.status != status:
                match = False
            if deadline and action.deadline and action.deadline != deadline: # Basic string match, would need date parsing for real use
                match = False
            if priority and action.priority != priority:
                match = False
            
            if match:
                filtered_actions.append(action.dict())
        
        logger.info(f"Found {len(filtered_actions)} actionable items for document {document_id}.")
        return filtered_actions

    def save_metadata(self, metadata: Dict[str, Any], output_path: str):
        """Saves the extracted metadata to a JSON file."""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=4)
            logger.info(f"Metadata saved to {output_path}")
        except IOError as e:
            logger.error(f"Failed to save metadata to {output_path}: {e}")
            raise DocumentProcessingError(f"Could not save metadata: {e}") 