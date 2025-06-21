from flask import jsonify

class FactifyException(Exception):
    """Base exception for the Factify application."""
    def __init__(self, message, status_code=500, code="UNKNOWN_ERROR", details=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or {}

    def to_dict(self):
        """Converts the exception to a dictionary suitable for API response."""
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details
        }

class DocumentProcessingError(FactifyException):
    """Exception raised for errors during document processing (e.g., PDF parsing, LLM interaction)."""
    def __init__(self, message="Document processing failed.", details=None):
        super().__init__(message, status_code=500, code="DOCUMENT_PROCESSING_FAILED", details=details)

class LLMAPIError(FactifyException):
    """Exception raised for errors interacting with the LLM API."""
    def __init__(self, message="LLM API request failed.", original_error=None, details=None):
        error_details = details or {}
        if original_error:
            error_details["original_error"] = str(original_error)
        super().__init__(message, status_code=503, code="LLM_API_ERROR", details=error_details)

class DocumentNotFoundError(FactifyException):
    """Exception raised when a requested document ID is not found."""
    def __init__(self, document_id, message="Document not found."):
        super().__init__(message, status_code=404, code="DOCUMENT_NOT_FOUND", details={"document_id": document_id})

class InvalidInputError(FactifyException):
    """Exception raised for invalid input data (e.g., malformed JSON, missing fields)."""
    def __init__(self, message="Invalid input provided.", details=None):
        super().__init__(message, status_code=400, code="INVALID_INPUT", details=details)

# Centralized error handler for Flask
def handle_factify_exception(error: FactifyException):
    """Handles custom Factify exceptions for Flask API responses."""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

def register_error_handlers(app):
    """Registers custom error handlers with the Flask application."""
    app.register_error_handler(FactifyException, handle_factify_exception)
    # You can register more specific error handlers if needed, e.g., for ValidationError
    # app.register_error_handler(404, lambda e: handle_factify_exception(DocumentNotFoundError("Resource not found."))) 