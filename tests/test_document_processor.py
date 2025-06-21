import unittest
from unittest.mock import Mock, patch
from core.document_processor import DocumentProcessor
from core.models import DocumentResult, DocumentClassification
from utils.exceptions import DocumentProcessingError

class TestDocumentProcessor(unittest.TestCase):
    """Basic tests for the DocumentProcessor class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.processor = DocumentProcessor()
    
    def test_processor_initialization(self):
        """Test that the DocumentProcessor initializes correctly."""
        self.assertIsInstance(self.processor, DocumentProcessor)
        self.assertIsNotNone(self.processor.llm_interface)
        self.assertEqual(len(self.processor.processed_documents), 0)
    
    @patch('core.document_processor.pypdf.PdfReader')
    def test_extract_text_from_pdf_success(self, mock_pdf_reader):
        """Test successful PDF text extraction."""
        # Mock the PDF reader
        mock_page = Mock()
        mock_page.extract_text.return_value = "Sample PDF text content"
        mock_reader_instance = Mock()
        mock_reader_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader_instance
        
        # Create a mock file path
        test_file_path = "test_document.pdf"
        
        with patch('builtins.open', unittest.mock.mock_open()):
            result = self.processor._extract_text_from_pdf(test_file_path)
        
        self.assertEqual(result, "Sample PDF text content")
    
    @patch('core.document_processor.pypdf.PdfReader')
    def test_extract_text_from_pdf_empty(self, mock_pdf_reader):
        """Test PDF text extraction with empty content."""
        # Mock the PDF reader to return empty text
        mock_page = Mock()
        mock_page.extract_text.return_value = ""
        mock_reader_instance = Mock()
        mock_reader_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader_instance
        
        test_file_path = "empty_document.pdf"
        
        with patch('builtins.open', unittest.mock.mock_open()):
            with self.assertRaises(DocumentProcessingError):
                self.processor._extract_text_from_pdf(test_file_path)
    
    def test_get_document_metadata_not_found(self):
        """Test retrieving metadata for non-existent document."""
        result = self.processor.get_document_metadata("non-existent-id")
        self.assertIsNone(result)
    
    def test_get_actionable_items_not_found(self):
        """Test retrieving actionable items for non-existent document."""
        result = self.processor.get_actionable_items("non-existent-id")
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main() 