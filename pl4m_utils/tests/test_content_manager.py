import pytest
from unittest.mock import patch, MagicMock
from pl4m_utils.content_manager import ContentManager, ContentManagerError
from datetime import datetime

class TestContentManagerBase:
    """
    Base test class for content managers.
    Not meant to be run directly - subclass for specific manager tests.
    """
    
    # Prevent pytest from trying to run tests from base class
    __test__ = False
    
    @pytest.fixture
    def mock_metadata_manager(self):
        """Mock MetadataManager methods."""
        with patch('pl4m_utils.content_manager.MetadataManager') as mock_mm:
            # Configure mock methods with complete metadata
            mock_doc = {
                'id': 'test-id',
                'title': 'Test Post',
                'description': 'Test Description',
                'tags': ['test'],
                'bucket': self.bucket_name,
                'blob_path': '2024/03/test.txt',
                'gcs_path': f'gs://{self.bucket_name}/2024/03/test.txt'
            }
            mock_mm.create_document.return_value = mock_doc
            mock_mm.read_document.return_value = mock_doc
            mock_mm.update_document.return_value = mock_doc
            mock_mm.soft_delete.return_value = True
            mock_mm.hard_delete_document.return_value = True
            mock_mm.restore_document.return_value = True
            yield mock_mm

    @pytest.fixture
    def manager(self, mock_storage_client, mock_metadata_manager):
        """Initialize content manager with mocked dependencies."""
        with patch('pl4m_utils.content_manager.storage.Client') as mock_client:
            mock_client.return_value = mock_storage_client
            manager = self.manager_class()
            return manager

    @pytest.fixture
    def valid_content_path(self):
        """Return a valid GCS path for the content type."""
        return f"gs://{self.bucket_name}/2024/03/test{self.valid_extension}"

    def test_generate_upload_url(self, manager):
        """Test generating upload URL."""
        url = manager.generate_upload_url(
            f"test{self.valid_extension}",
            self.content_type
        )
        assert url == "https://fake-signed-url"

    def test_generate_upload_url_invalid_extension(self, manager):
        """Test generating upload URL with invalid extension."""
        with pytest.raises(ValueError, match="Invalid file extension"):
            manager.generate_upload_url("test.invalid", "application/octet-stream")

    def test_validate_metadata(self, manager, mock_metadata):
        """Test metadata validation."""
        manager._validate_metadata(mock_metadata)
        
        # Test missing tags
        invalid_metadata = mock_metadata.copy()
        del invalid_metadata['tags']
        with pytest.raises(ValueError, match="must include 'tags'"):
            manager._validate_metadata(invalid_metadata)

    def test_delete_content(self, manager, mock_metadata):
        """Test content deletion."""
        # Setup mock for get_content
        with patch.object(manager, 'get_content') as mock_get:
            mock_get.return_value = {
                'id': 'test-id',
                'bucket': manager.BUCKET,
                'blob_path': '2024/03/test.txt'
            }
            
            # Test soft delete
            assert manager.delete_content('test-id') is True
            
            # Test hard delete
            assert manager.delete_content('test-id', hard_delete=True) is True

    def test_restore_content(self, manager):
        """Test content restoration."""
        assert manager.restore_content('test-id') is True 

class TestContentManager(TestContentManagerBase):
    """Direct tests for ContentManager."""
    
    __test__ = True
    manager_class = ContentManager
    bucket_name = "test-bucket"
    valid_extension = ".txt"
    content_type = "text/plain"

    @pytest.fixture
    def manager(self):
        """Override to provide required init args."""
        return ContentManager(
            collection="test-collection",
            bucket=self.bucket_name,
            valid_extensions={self.valid_extension}
        )

    def test_init(self):
        """Test ContentManager initialization."""
        manager = ContentManager(
            collection="test-collection",
            bucket="test-bucket",
            valid_extensions={'.txt'}
        )
        assert manager.COLLECTION == "test-collection"
        assert manager.BUCKET == "test-bucket"
        assert manager.VALID_EXTENSIONS == {'.txt'}

    def test_parse_gcs_path(self):
        """Test GCS path parsing."""
        bucket, path = ContentManager._parse_gcs_path("gs://test-bucket/path/to/file.txt")
        assert bucket == "test-bucket"
        assert path == "path/to/file.txt"

        with pytest.raises(ValueError, match="must start with gs://"):
            ContentManager._parse_gcs_path("invalid://path")

    def test_generate_file_path(self, manager):
        """Test file path generation."""
        path = manager._generate_file_path("test.txt")
        # Should match yyyy/mm/filename pattern
        assert len(path.split('/')) == 3
        assert path.endswith("test.txt")

    def test_validate_extension(self, manager):
        """Test file extension validation."""
        manager._validate_extension("test.txt")
        
        with pytest.raises(ValueError, match="Invalid file extension"):
            manager._validate_extension("test.invalid")

    def test_validate_metadata_empty(self, manager):
        """Test metadata validation with empty metadata."""
        with pytest.raises(ValueError, match="must be a dictionary"):
            manager._validate_metadata(None)

    def test_validate_metadata_no_tags(self, manager):
        """Test metadata validation without tags."""
        with pytest.raises(ValueError, match="must include 'tags'"):
            manager._validate_metadata({'description': 'test'})

    def test_validate_metadata_invalid_tags(self, manager):
        """Test metadata validation with invalid tags type."""
        with pytest.raises(ValueError, match="must include 'tags'"):
            manager._validate_metadata({'tags': 'not a list'}) 