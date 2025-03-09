from typing import Optional, Dict, Any
from pl4m_utils.metadata_manager import MetadataManager, MetadataManagerError
from pl4m_utils.content_manager import ContentManager, ContentManagerError
from pl4m_utils.config import get_collection_name
from datetime import datetime

class ImageManager(ContentManager):
    """
    Manager for image content with specific metadata requirements.
    
    This class extends ContentManager to handle image-specific operations and metadata.
    It enforces image file types, handles image-specific metadata like taken_at dates,
    and manages image files in GCS with their corresponding Firestore records.
    """

    def __init__(self):
        """Initialize the image manager with image-specific settings."""
        super().__init__(
            collection=get_collection_name("images"),
            content_type="images",
            valid_extensions={'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        )

    def create_image(self, gcs_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new image record with metadata and GCS path.
        
        Args:
            gcs_path: Full GCS path to the image (gs://bucket/path/to/image.jpg)
            metadata: Additional metadata for the image including:
                     - tags (required): List or set of tags
                     - taken_at (optional): datetime object
                     - description (optional): Image description
            
        Returns:
            Dictionary containing the complete image record
            
        Raises:
            ContentManagerError: If record creation fails
            ValueError: If metadata or path is invalid
        """
        try:
            self._validate_metadata(metadata)  # Base class validation for tags

            if not isinstance(metadata, dict):
                raise ValueError("Metadata must be a dictionary")

            bucket_name, blob_path = self._parse_gcs_path(gcs_path)
            if bucket_name != self.BUCKET:
                raise ValueError(f"Invalid bucket: {bucket_name}")
            
            # Validate taken_at if provided
            if 'taken_at' in metadata:
                if not isinstance(metadata['taken_at'], datetime):
                    raise ValueError("taken_at must be a datetime object")
            
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_path)
            if not blob.exists():
                raise ValueError(f"Image file does not exist: {gcs_path}")
            
            image_data = metadata.copy()
            image_data.update({
                'gcs_path': gcs_path,
                'bucket': bucket_name,
                'blob_path': blob_path,
                'size_bytes': blob.size,
                'content_type': blob.content_type
            })
            
            return MetadataManager.create_document(self.COLLECTION, image_data)
        except Exception as e:
            raise ContentManagerError(f"Failed to create image record: {str(e)}")

    def upload_new_image(self, filename: str, content: bytes, metadata: Dict[str, Any], 
                         date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Upload a new image with content and metadata in one operation.
        
        Args:
            filename: Name of the image file
            content: Image content as bytes
            metadata: Image metadata
            date: Optional date for path generation (defaults to today)
            
        Returns:
            Complete image record
        """
        try:
            self._validate_extension(filename)
            self._validate_metadata(metadata)
            
            # Validate taken_at if provided
            if 'taken_at' in metadata:
                if not isinstance(metadata['taken_at'], datetime):
                    raise ValueError("taken_at must be a datetime object")
            
            # Determine content type based on file extension
            ext = filename.lower().split('.')[-1]
            content_type_map = {
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'gif': 'image/gif',
                'webp': 'image/webp'
            }
            content_type = content_type_map.get(ext, 'application/octet-stream')
            
            # Generate path and upload file
            file_path = self._generate_file_path(filename, date)
            bucket = self.storage_client.bucket(self.BUCKET)
            blob = bucket.blob(file_path)
            
            blob.upload_from_string(content, content_type=content_type)
            
            # Create metadata record
            gcs_path = f"gs://{self.BUCKET}/{file_path}"
            image_data = metadata.copy()
            image_data.update({
                'gcs_path': gcs_path,
                'bucket': self.BUCKET,
                'blob_path': file_path,
                'size_bytes': len(content),
                'content_type': content_type
            })
            
            return MetadataManager.create_document(self.COLLECTION, image_data)
        except Exception as e:
            raise ContentManagerError(f"Failed to upload new image: {str(e)}")
