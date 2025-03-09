from pl4m_utils.content_manager import ContentManager, ContentManagerError
from pl4m_utils.metadata_manager import MetadataManager
from pl4m_utils.config import get_collection_name
from typing import Dict, Any, Optional
from datetime import datetime

class BlogManager(ContentManager):
    """
    Manager for blog content with markdown-specific handling.
    
    This class extends ContentManager to handle blog post operations and metadata.
    It enforces markdown file types, manages required blog metadata fields like
    title and description, and handles content updates for blog posts.
    """

    def __init__(self):
        """Initialize the blog manager with markdown-specific settings."""
        super().__init__(
            collection=get_collection_name("blog"),
            content_type="blog",
            valid_extensions={'.md', '.markdown'}
        )

    def create_post(self, gcs_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new blog post record with metadata and content.
        
        Args:
            gcs_path: Full GCS path to the markdown file
            metadata: Blog post metadata including:
                     - title (required): Post title
                     - description (required): Post description
                     - tags (required): List or set of tags
                     
        Returns:
            Dictionary containing the complete blog post record
            
        Raises:
            ContentManagerError: If record creation fails
            ValueError: If metadata or path is invalid
        """
        try:
            self._validate_metadata(metadata)  # Base class validation

            # Additional blog-specific validation
            required_fields = {'title', 'description'}
            missing_fields = required_fields - metadata.keys()
            if missing_fields:
                raise ValueError(f"Missing required metadata fields: {missing_fields}")

            bucket_name, blob_path = self._parse_gcs_path(gcs_path)
            if bucket_name != self.BUCKET:
                raise ValueError(f"Invalid bucket: {bucket_name}")
            
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_path)
            if not blob.exists():
                raise ValueError(f"Blog post file does not exist: {gcs_path}")
            
            post_data = metadata.copy()
            post_data.update({
                'gcs_path': gcs_path,
                'bucket': bucket_name,
                'blob_path': blob_path,
                'size_bytes': blob.size,
                'content_type': 'text/markdown'
            })
            
            return MetadataManager.create_document(self.COLLECTION, post_data)
        except Exception as e:
            raise ContentManagerError(f"Failed to create blog post record: {str(e)}")

    def update_post(self, post_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update blog post metadata and optionally content."""
        try:
            # Prevent updating critical fields
            protected_fields = {'gcs_path', 'bucket', 'blob_path', 'id', 'created_at'}
            invalid_fields = protected_fields.intersection(updates.keys())
            if invalid_fields:
                raise ValueError(f"Cannot update protected fields: {invalid_fields}")
            
            return MetadataManager.update_document(self.COLLECTION, post_id, updates)
        except Exception as e:
            raise ContentManagerError(f"Failed to update blog post: {str(e)}")

    def update_post_content(self, post_id: str, new_content: str) -> Dict[str, Any]:
        """
        Update the markdown content of a blog post.
        
        Args:
            post_id: ID of the blog post
            new_content: New markdown content
            
        Returns:
            Updated blog post record
        """
        return self.update_content(post_id, new_content, 'text/markdown')

    def upload_new_post(self, filename: str, content: str, metadata: Dict[str, Any], 
                        date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Upload a new blog post with content and metadata in one operation.
        
        Args:
            filename: Name of the markdown file
            content: Markdown content as string
            metadata: Blog post metadata
            date: Optional date for path generation (defaults to today)
            
        Returns:
            Complete blog post record
        """
        try:
            self._validate_extension(filename)
            self._validate_metadata(metadata)
            
            # Additional blog-specific validation
            required_fields = {'title', 'description'}
            missing_fields = required_fields - metadata.keys()
            if missing_fields:
                raise ValueError(f"Missing required metadata fields: {missing_fields}")
            
            # Generate path and upload file
            file_path = self._generate_file_path(filename, date)
            bucket = self.storage_client.bucket(self.BUCKET)
            blob = bucket.blob(file_path)
            
            content_type = 'text/markdown'
            blob.upload_from_string(content, content_type=content_type)
            
            # Create metadata record
            gcs_path = f"gs://{self.BUCKET}/{file_path}"
            post_data = metadata.copy()
            post_data.update({
                'gcs_path': gcs_path,
                'bucket': self.BUCKET,
                'blob_path': file_path,
                'size_bytes': len(content.encode('utf-8')),
                'content_type': content_type
            })
            
            return MetadataManager.create_document(self.COLLECTION, post_data)
        except Exception as e:
            raise ContentManagerError(f"Failed to upload new blog post: {str(e)}")
