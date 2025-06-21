import uuid
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ValidationError, field_validator

class DocumentClassification(BaseModel):
    """Represents the classification of a document."""
    type: str = Field(..., description="The classified type of the document (e.g., 'invoice', 'contract', 'report').")
    confidence: float = Field(..., ge=0.0, le=1.0, description="A confidence score for the classification, between 0 and 1.")

class DocumentMetadata(BaseModel):
    """Base model for extracted metadata, adaptable per document type."""
    # This will be dynamically populated based on document type
    pass

class DocumentResult(BaseModel):
    """The complete structured output for a processed document."""
    document_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="A unique identifier for the processed document.")
    filename: str = Field(..., description="The original filename of the document.")
    classification: DocumentClassification = Field(..., description="The classification details of the document.")
    metadata: Dict[str, Any] = Field(..., description="A dictionary containing type-specific extracted metadata.")
    processing_status: str = Field("success", description="The status of the document processing ('success', 'failed', 'partial').")
    error_message: Optional[str] = Field(None, description="Detailed error message if processing failed or was partial.")

    @field_validator('metadata')
    @classmethod
    def validate_metadata_structure(cls, v, info):
        """
        Custom validation to ensure metadata structure aligns with expected document types.
        This is a conceptual validator. Actual validation logic would be more complex,
        potentially using a Pydantic model for each document type.
        """
        # In Pydantic V2, we access other fields through info.data
        values = info.data if info.data else {}
        if 'classification' in values and values['classification']:
            doc_type = values['classification'].type
            # In a real scenario, you'd load a specific Pydantic model for `doc_type`
            # and validate `v` against it. For now, this is a placeholder.
            # Example: if doc_type == 'invoice', validate against InvoiceMetadata model.
            pass # Placeholder for dynamic validation
        return v

class ActionableItem(BaseModel):
    """Represents an actionable item extracted from a document."""
    item_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique ID for the actionable item.")
    description: str = Field(..., description="A description of the actionable item.")
    status: str = Field("pending", description="Current status (e.g., 'pending', 'completed', 'overdue').")
    deadline: Optional[str] = Field(None, description="Optional deadline for the action, in YYYY-MM-DD format.")
    priority: str = Field("medium", description="Priority level (e.g., 'low', 'medium', 'high').")
    source_field: Optional[str] = Field(None, description="The metadata field from which this action was derived.")

class ApiErrorResponse(BaseModel):
    """Standardized error response for the API."""
    code: str = Field(..., description="A unique error code.")
    message: str = Field(..., description="A human-readable error message.")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details.")

# Example of how you might define specific metadata models (not used directly in DocumentMetadata yet)
class InvoiceMetadata(BaseModel):
    vendor: Optional[str]
    amount: Optional[str]
    due_date: Optional[str]
    line_items: List[Dict[str, Any]] = []

class ContractMetadata(BaseModel):
    parties: List[str] = []
    effective_date: Optional[str]
    termination_date: Optional[str]
    key_terms: List[str] = [] 