import pytest
from unittest.mock import MagicMock, patch
from google.cloud import storage
from datetime import datetime

@pytest.fixture
def mock_storage_client():
    """Provides a mocked GCS client."""
    mock_client = MagicMock(spec=storage.Client)
    
    # Setup mock bucket and blob
    mock_bucket = MagicMock(spec=storage.Bucket)
    mock_blob = MagicMock(spec=storage.Blob)
    
    # Configure mock blob with more specific responses
    mock_blob.exists.return_value = True  # Default to file exists
    mock_blob.size = 1024
    mock_blob.content_type = None  # Let specific tests set this
    
    # Mock the signed URL generation
    def fake_signed_url(**kwargs):
        return "https://fake-signed-url"
    mock_blob.generate_signed_url = fake_signed_url
    
    # Mock upload
    mock_blob.upload_from_string.return_value = None
    
    # Configure mock bucket
    mock_bucket.blob.return_value = mock_blob
    mock_client.bucket.return_value = mock_bucket
    
    # Mock credentials
    mock_client._credentials = MagicMock()
    mock_client._credentials.sign_bytes = lambda x: b'fake-signature'
    
    return mock_client

@pytest.fixture
def mock_metadata():
    """Provides base metadata for content tests."""
    return {
        'tags': ['test', 'fixture'],
        'description': 'Test content',
        'title': 'Test Title',  # Add required fields
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'deleted_at': None,
        'id': 'test-id',
        'bucket': 'tylers-platform-docs',
        'blob_path': '2024/03/test.txt',
        'gcs_path': 'gs://tylers-platform-docs/2024/03/test.txt'
    } 