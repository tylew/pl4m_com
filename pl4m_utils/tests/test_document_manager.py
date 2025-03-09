import pytest
from pl4m_utils.document_manager import DocumentManager
from .test_content_manager import TestContentManagerBase

class TestDocumentManager(TestContentManagerBase):
    """Test cases for DocumentManager."""
    
    __test__ = True
    manager_class = DocumentManager
    bucket_name = "tylers-platform-docs"
    valid_extension = ".pdf"
    content_type = "application/pdf"

    @pytest.fixture
    def valid_document_metadata(self, mock_metadata):
        """Provide valid document metadata."""
        mock_metadata.update({
            'title': 'Test Document',
            'description': 'A test document',
            'author': 'Test Author',
            'page_count': 42
        })
        return mock_metadata

    def test_create_document(self, manager, valid_document_metadata, valid_content_path):
        """Test document creation."""
        doc = manager.create_document(valid_content_path, valid_document_metadata)
        assert doc is not None
        assert doc.get('title') == 'Test Document'

    def test_create_document_missing_required(self, manager, mock_metadata, valid_content_path):
        """Test document creation with missing required fields."""
        with pytest.raises(ValueError, match="Missing required metadata fields"):
            manager.create_document(valid_content_path, mock_metadata)

    def test_replace_document(self, manager):
        """Test document replacement."""
        updated = manager.replace_document('test-id', b'New PDF content')
        assert updated is not None 