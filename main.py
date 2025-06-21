import os
import argparse
from config.settings import DOC_INPUT_DIR, DOC_OUTPUT_DIR
from core.document_processor import DocumentProcessor
from utils.logger import setup_logging
from utils.exceptions import DocumentProcessingError

# Set up logging for the main script
logger = setup_logging(__name__)

def process_single_document(file_path: str, processor: DocumentProcessor):
    """Processes a single document and saves its metadata."""
    try:
        logger.info(f"Processing document: {os.path.basename(file_path)}")
        metadata = processor.process_document(file_path)

        output_filename = os.path.join(DOC_OUTPUT_DIR, f"{metadata['document_id']}.json")
        processor.save_metadata(metadata, output_filename)
        logger.info(f"Successfully processed {os.path.basename(file_path)}. Metadata saved to {output_filename}")
        return metadata
    except DocumentProcessingError as e:
        logger.error(f"Failed to process {os.path.basename(file_path)}: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred while processing {os.path.basename(file_path)}: {e}", exc_info=True)
        return None

def main():
    parser = argparse.ArgumentParser(description="Process documents and extract intelligent metadata.")
    parser.add_argument(
        "--document",
        type=str,
        help="Path to a single document to process. If not provided, all documents in DOC_INPUT_DIR will be processed."
    )
    args = parser.parse_args()

    # Ensure output directory exists
    os.makedirs(DOC_OUTPUT_DIR, exist_ok=True)

    processor = DocumentProcessor()

    if args.document:
        if not os.path.exists(args.document):
            logger.error(f"Document not found at: {args.document}")
            return
        process_single_document(args.document, processor)
    else:
        logger.info(f"Processing all documents in input directory: {DOC_INPUT_DIR}")
        document_files = [
            f for f in os.listdir(DOC_INPUT_DIR)
            if f.endswith('.pdf') # or other supported formats
        ]

        if not document_files:
            logger.warning(f"No documents found in {DOC_INPUT_DIR} to process.")
            return

        for filename in document_files:
            file_path = os.path.join(DOC_INPUT_DIR, filename)
            process_single_document(file_path, processor)

if __name__ == "__main__":
    main() 