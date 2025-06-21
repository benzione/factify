import os
import sys
from pathlib import Path

# Add the parent directory to the Python path so imports work correctly
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

from flask import Flask, jsonify
from flask_restful import Api
from utils.logger import setup_logging
from utils.exceptions import register_error_handlers, FactifyException
from api.routes import initialize_routes
from core.document_processor import DocumentProcessor # Import DocumentProcessor

logger = setup_logging(__name__)

def create_app():
    app = Flask(__name__)
    api = Api(app)

    # Register error handlers
    register_error_handlers(app)

    # Initialize DocumentProcessor and pass it to routes
    # This acts as a simple in-memory database for processed documents
    app.document_processor = DocumentProcessor()

    # Initialize API routes
    initialize_routes(api, app.document_processor)

    # Basic health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy", "message": "Factify API is running!"}), 200

    logger.info("Factify API application created and routes initialized.")
    return app

if __name__ == '__main__':
    # Ensure a 'documents_to_process' directory exists for input files
    # Create dummy files for demonstration if they don't exist
    input_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "documents_to_process")
    os.makedirs(input_dir, exist_ok=True)

    dummy_invoice_path = os.path.join(input_dir, "invoice_sample.pdf")
    dummy_contract_path = os.path.join(input_dir, "contract_sample.pdf")
    dummy_earnings_path = os.path.join(input_dir, "earnings_sample.pdf")

    if not os.path.exists(dummy_invoice_path):
        logger.warning(f"No invoice_sample.pdf found in {input_dir}. Please add sample PDFs to test.")
        # Create a simple dummy PDF (requires reportlab)
        try:
            from reportlab.pdfgen import canvas as pdf_canvas
            from reportlab.lib.pagesizes import letter

            c = pdf_canvas.Canvas(dummy_invoice_path, pagesize=letter)
            c.drawString(100, 750, "Invoice #2024-001")
            c.drawString(100, 730, "Vendor: Acme Corp")
            c.drawString(100, 710, "Amount Due: $1500.00")
            c.drawString(100, 690, "Due Date: 2024-07-15")
            c.drawString(100, 670, "Line Item: Consulting Services - 10 hrs @ $150/hr")
            c.save()
            logger.info(f"Created a dummy invoice PDF: {dummy_invoice_path}")
        except ImportError:
            logger.warning("ReportLab not installed. Cannot create dummy PDF. Please install with 'pip install reportlab' or manually place sample PDFs.")
        except Exception as e:
            logger.error(f"Error creating dummy PDF: {e}")

    if not os.path.exists(dummy_contract_path):
        logger.warning(f"No contract_sample.pdf found in {input_dir}. Please add sample PDFs to test.")

    if not os.path.exists(dummy_earnings_path):
        logger.warning(f"No earnings_sample.pdf found in {input_dir}. Please add sample PDFs to test.")


    app = create_app()
    app.run(debug=True, port=5000) 