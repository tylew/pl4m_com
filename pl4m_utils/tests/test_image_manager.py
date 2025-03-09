import pytest
from pl4m_utils.image_manager import ImageManager
from .test_content_manager import TestContentManagerBase
from datetime import datetime

class TestImageManager(TestContentManagerBase):
    """Test cases for ImageManager."""
    
    __test__ = True
    manager_class = ImageManager
    bucket_name = "tylers-platform-images"
    valid_extension = ".jpg"
    content_type = "image/jpeg"

    @pytest.fixture
    def valid_image_metadata(self, mock_metadata):
        """Provide valid image metadata."""
        mock_metadata.update({
            'taken_at': datetime.utcnow(),
            'description': 'Test image'
        })
        return mock_metadata

    def test_create_image(self, manager, valid_image_metadata, valid_content_path):
        """Test image creation."""
        image = manager.create_image(valid_content_path, valid_image_metadata)
        assert image is not None
        assert 'taken_at' in image

    def test_create_image_invalid_taken_at(self, manager, valid_image_metadata, valid_content_path):
        """Test image creation with invalid taken_at."""
        valid_image_metadata['taken_at'] = "not a datetime"
        with pytest.raises(ValueError, match="taken_at must be a datetime"):
            manager.create_image(valid_content_path, valid_image_metadata) 