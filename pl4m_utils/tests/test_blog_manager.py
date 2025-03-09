import pytest
from pl4m_utils.blog_manager import BlogManager
from .test_content_manager import TestContentManagerBase

class TestBlogManager(TestContentManagerBase):
    """Test cases for BlogManager."""
    
    __test__ = True  # Enable tests for this class
    manager_class = BlogManager
    bucket_name = "tylers-platform-docs"
    valid_extension = ".md"
    content_type = "text/markdown"

    @pytest.fixture
    def valid_blog_metadata(self, mock_metadata):
        """Provide valid blog post metadata."""
        mock_metadata.update({
            'title': 'Test Post',
            'description': 'A test blog post'
        })
        return mock_metadata

    def test_create_post(self, manager, valid_blog_metadata, valid_content_path, mock_metadata_manager):
        """Test blog post creation."""
        # Ensure metadata has required fields
        valid_blog_metadata.update({
            'title': 'Test Post',
            'description': 'A test blog post',
            'tags': ['test']
        })
        
        post = manager.create_post(valid_content_path, valid_blog_metadata)
        assert post is not None
        assert post.get('title') == 'Test Post'
        mock_metadata_manager.create_document.assert_called_once()

    def test_create_post_missing_required(self, manager, mock_metadata, valid_content_path):
        """Test blog post creation with missing required fields."""
        with pytest.raises(ValueError, match="Missing required metadata fields"):
            manager.create_post(valid_content_path, mock_metadata)

    def test_update_post_content(self, manager):
        """Test updating blog post content."""
        updated = manager.update_post_content('test-id', '# New Content')
        assert updated is not None 