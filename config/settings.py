import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- API Keys ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file. Please set it.")

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC_INPUT_DIR = os.path.join(BASE_DIR, "documents_to_process") # You'll need to create this folder and place your PDFs here
DOC_OUTPUT_DIR = os.path.join(BASE_DIR, "output")
LOG_FILE_PATH = os.path.join(BASE_DIR, "app.log")
CACHE_DIR = os.path.join(BASE_DIR, ".cache") # Directory for caching LLM responses

# --- LLM Settings ---
LLM_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")  # Default to gemini-1.5-flash if not set
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1024"))

# --- Caching Settings ---
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() in ["true", "1", "yes", "on"]
CACHE_EXPIRATION_TIME_SECONDS = int(os.getenv("CACHE_EXPIRATION_TIME_SECONDS", "3600"))  # Default 1 hour

# --- Document Specific Settings (example, expand as needed) ---
# Define expected metadata fields per document type
DOCUMENT_TYPES = {
    "invoice": {
        "classification_keywords": ["invoice", "bill", "receipt"],
        "metadata_fields": ["vendor", "amount", "due_date", "line_items"],
        "semantic_description": {
            "vendor": "The name of the company or individual issuing the invoice.",
            "amount": "The total amount due on the invoice, including currency.",
            "due_date": "The date by which the invoice payment is expected.",
            "line_items": "A list of individual products or services with their quantities and prices."
        }
    },
    "contract": {
        "classification_keywords": ["contract", "agreement", "legal document"],
        "metadata_fields": ["parties", "effective_date", "termination_date", "key_terms"],
        "semantic_description": {
            "parties": "The names of all entities involved and bound by the contract.",
            "effective_date": "The date when the terms of the contract officially begin.",
            "termination_date": "The date when the contract is set to expire, if applicable.",
            "key_terms": "A summary of crucial clauses, conditions, or definitions within the contract."
        }
    },
    "report": {
        "classification_keywords": ["report", "quarterly report", "financial statement"],
        "metadata_fields": ["reporting_period", "key_metrics", "executive_summary"],
        "semantic_description": {
            "reporting_period": "The period (e.g., quarter, year) that the report covers.",
            "key_metrics": "Important quantitative measures and performance indicators.",
            "executive_summary": "A brief overview of the report's main findings and conclusions."
        }
    },
    "other": {
        "classification_keywords": ["document", "letter", "memo", "presentation", "manual", "form"],
        "metadata_fields": ["document_title", "author", "date_created", "subject", "key_points", "document_purpose"],
        "semantic_description": {
            "document_title": "The title or main heading of the document.",
            "author": "The person or organization who created or authored the document.",
            "date_created": "The date when the document was created or issued.",
            "subject": "The main subject or topic that the document addresses.",
            "key_points": "The most important points, findings, or conclusions mentioned in the document.",
            "document_purpose": "The primary purpose or intended use of the document."
        }
    }
} 