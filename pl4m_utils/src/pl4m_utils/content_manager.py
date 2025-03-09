from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Set, Union
from pl4m_utils.metadata_manager import MetadataManager, MetadataManagerError
from pl4m_utils.config import (
    get_bucket_name, get_content_type_config, 
    get_collection_name, get_mime_type
)
from google.cloud import storage
from urllib.parse import urlparse

class ContentManagerError(Exception):
    """Base exception for content management errors."""
    pass

class ContentManager:
    """
    Unified manager for GCS-stored content with Firestore metadata.
    
    This class handles the storage of content in Google Cloud Storage while using
    MetadataManager to track metadata in Firestore. It provides:
    - Content upload and management
    - Metadata validation and storage
    - URL generation for uploads
    - Content type-specific configurations
    """
    
    storage_client = storage.Client()

    def __init__(self, content_type: str):
        """Initialize content manager for a specific content type."""
        self.content_type = content_type
        self.config = get_content_type_config(content_type)
        self.collection = get_collection_name(content_type)
        self.bucket = get_bucket_name()
        self.valid_extensions = self.config["valid_extensions"]
        self.required_metadata = self.config["required_metadata"]
        self.optional_metadata = self.config.get("optional_metadata", set())
        self.metadata_manager = MetadataManager()

    @staticmethod
    def _parse_gcs_path(gcs_path: str) -> tuple[str, str]:
        """Parse GCS path into bucket and blob path."""
        if not gcs_path.startswith("gs://"):
            raise ValueError("GCS path must start with gs://")
            
        parsed = urlparse(gcs_path)
        bucket_name = parsed.netloc
        blob_path = parsed.path.lstrip('/')
        
        if not bucket_name or not blob_path:
            raise ValueError("Invalid GCS path format")
            
        return bucket_name, blob_path

    def _validate_extension(self, filename: str) -> None:
        """Validate file extension against allowed types."""
        ext = f".{filename.lower().split('.')[-1]}"
        if ext not in self.valid_extensions:
            raise ValueError(f"Invalid file extension: {ext}. Allowed: {self.valid_extensions}")

    def _validate_metadata(self, metadata: Dict[str, Any]) -> None:
        """Validate metadata against required and optional fields."""
        if not isinstance(metadata, dict):
            raise ValueError("Metadata must be a dictionary")
        
        required_fields = {field for field in self.required_metadata 
                         if field != 'last_modified'}
        missing_fields = required_fields - metadata.keys()
        if missing_fields:
            raise ValueError(f"Missing required metadata fields: {missing_fields}")
            
        invalid_fields = set(metadata.keys()) - (required_fields | self.optional_metadata)
        if invalid_fields:
            raise ValueError(f"Invalid metadata fields: {invalid_fields}")

        # Type validations for common fields
        type_validations = {
            'tags': (list, set),
            'taken_at': datetime,
            'publish_date': datetime,
            'created_date': datetime
        }
        
        for field, expected_type in type_validations.items():
            if field in metadata and not isinstance(metadata[field], expected_type):
                raise ValueError(f"'{field}' must be of type {expected_type}")

    def _generate_file_path(self, filename: str, date: Optional[datetime] = None) -> str:
        """Generate path structure: {YYYY}/{MM}/{DD}/{content_type}/{filename}"""
        if not filename or '/' in filename:
            raise ValueError("Invalid filename")
        target_date = date or datetime.utcnow()
        return f"{target_date.year:04d}/{target_date.month:02d}/{target_date.day:02d}/{self.content_type}/{filename}"

    def generate_upload_url(self, filename: str, date: Optional[datetime] = None, 
                          allow_overwrite: bool = False) -> str:
        """Generate signed upload URL for GCS."""
        try:
            self._validate_extension(filename)
            file_path = self._generate_file_path(filename, date)
            content_type = get_mime_type(self.content_type, filename)
            
            bucket = self.storage_client.bucket(self.bucket)
            blob = bucket.blob(file_path)
            
            if not allow_overwrite and blob.exists():
                raise ValueError(f"File already exists at path: {file_path}")
            
            return blob.generate_signed_url(
                version="v4",
                method="PUT",
                expiration=timedelta(minutes=15),
                content_type=content_type,
            )
        except Exception as e:
            raise ContentManagerError(f"Failed to generate upload URL: {str(e)}")

    def get_content(self, content_id: str, include_deleted: bool = False) -> Optional[Dict[str, Any]]:
        """Get content metadata by ID."""
        try:
            return self.metadata_manager.read_document(self.collection, content_id, include_deleted)
        except MetadataManagerError as e:
            raise ContentManagerError(f"Failed to retrieve content: {str(e)}")

    def list_content(self, page: int = 1, per_page: int = 20,
                    filters: Optional[List[tuple]] = None,
                    sort_by: str = 'created_at', sort_order: str = 'desc') -> Dict[str, Any]:
        """List content with pagination, filtering and sorting."""
        try:
            filter_dicts = [{'field': f, 'op': o, 'value': v} for f, o, v in (filters or [])]
            
            return self.metadata_manager.list_documents(
                collection=self.collection,
                include_deleted=False,
                order_by=sort_by,
                descending=sort_order.lower() == 'desc',
                filters=filter_dicts,
                page=page,
                per_page=per_page
            )
        except MetadataManagerError as e:
            print(f"Collection: {self.collection}")
            print(f"Filters: {filters}")
            print(f"Order by: {sort_by}, Descending: {sort_order.lower() == 'desc'}")
            print(f"Page: {page}, Per Page: {per_page}")

            raise ContentManagerError(f"Failed to list content: {str(e)}")

    def update_content(self, content_id: str, new_content: Union[str, bytes]) -> Dict[str, Any]:
        """Update the content of a GCS file and its metadata."""
        try:
            content = self.get_content(content_id)
            if not content:
                raise ValueError(f"Content {content_id} not found")

            content_type = content.get('content_type') or get_mime_type(
                self.content_type, content['blob_path'].split('/')[-1]
            )

            bucket = self.storage_client.bucket(content['bucket'])
            blob = bucket.blob(content['blob_path'])
            
            if isinstance(new_content, str):
                new_content = new_content.encode('utf-8')
            
            blob.upload_from_string(new_content, content_type=content_type)
            
            updates = {'size_bytes': len(new_content)}
            if 'last_modified' in self.required_metadata:
                updates['last_modified'] = datetime.utcnow()
            
            return self.metadata_manager.update_document(self.collection, content_id, updates)
        except Exception as e:
            raise ContentManagerError(f"Failed to update content: {str(e)}")

    def update_metadata(self, content_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update content metadata."""
        try:
            protected_fields = {'gcs_path', 'bucket', 'blob_path', 'id', 'created_at', 'content_type'}
            invalid_fields = protected_fields.intersection(updates.keys())
            if invalid_fields:
                raise ValueError(f"Cannot update protected fields: {invalid_fields}")
            
            update_data = updates.copy()
            if 'last_modified' in self.required_metadata:
                update_data['last_modified'] = datetime.utcnow()
            
            return self.metadata_manager.update_document(self.collection, content_id, update_data)
        except MetadataManagerError as e:
            raise ContentManagerError(f"Failed to update metadata: {str(e)}")

    def upload_new_content(self, filename: str, content: Union[str, bytes], 
                         metadata: Dict[str, Any], date: Optional[datetime] = None,
                         creation_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Upload new content with metadata in one operation."""
        try:
            self._validate_extension(filename)
            self._validate_metadata(metadata)
            
            file_path = self._generate_file_path(filename, date)
            content_type = get_mime_type(self.content_type, filename)
            
            if isinstance(content, str):
                content = content.encode('utf-8')
            
            bucket = self.storage_client.bucket(self.bucket)
            blob = bucket.blob(file_path)
            blob.upload_from_string(content, content_type=content_type)
            
            content_data = metadata.copy()
            content_data.update({
                'gcs_path': f"gs://{self.bucket}/{file_path}",
                'bucket': self.bucket,
                'blob_path': file_path,
                'size_bytes': len(content),
                'content_type': content_type
            })
            
            if 'last_modified' in self.required_metadata:
                content_data['last_modified'] = datetime.utcnow()
            
            custom_timestamps = {'created_at': creation_date} if creation_date else None
            
            return self.metadata_manager.create_document(
                self.collection, 
                content_data,
                custom_timestamps=custom_timestamps
            )
        except Exception as e:
            raise ContentManagerError(f"Failed to upload new content: {str(e)}")

    def delete_content(self, content_id: str, hard_delete: bool = False) -> bool:
        """Delete content record and optionally its GCS file."""
        try:
            content = self.get_content(content_id, include_deleted=True)
            if not content:
                raise ValueError(f"Content {content_id} not found")

            if hard_delete:
                bucket = self.storage_client.bucket(content['bucket'])
                blob = bucket.blob(content['blob_path'])
                if blob.exists():
                    blob.delete()
                return self.metadata_manager.hard_delete_document(self.collection, content_id)
            else:
                return self.metadata_manager.soft_delete(self.collection, content_id)
        except Exception as e:
            raise ContentManagerError(f"Failed to delete content: {str(e)}")

    def restore_content(self, content_id: str) -> bool:
        """Restore a soft-deleted content record."""
        try:
            return self.metadata_manager.restore_document(self.collection, content_id)
        except MetadataManagerError as e:
            raise ContentManagerError(f"Failed to restore content: {str(e)}")

    def get_available_tags(self) -> List[str]:
        """
        Get a list of all unique tags used in the collection from non-deleted documents.
        
        Returns:
            List[str]: Sorted list of unique tags
            
        Raises:
            ContentManagerError: If tag retrieval fails
        """
        try:
            return self.metadata_manager.get_distinct_tags(self.collection, include_deleted=False)
        except MetadataManagerError as e:
            raise ContentManagerError(f"Failed to get available tags: {str(e)}")

    def update_content_tags(self, content_id: str, tags: List[str], operation: str = 'set') -> Dict[str, Any]:
        """
        Modify tags for a specific content item.
        
        Args:
            content_id: ID of the content to update
            tags: List of tags to add/remove/set
            operation: Type of operation ('add', 'remove', or 'set')
            
        Returns:
            Dict[str, Any]: Updated content metadata
            
        Raises:
            ContentManagerError: If tag update fails
            ValueError: If operation is invalid or content not found
        """
        try:
            # Verify content exists and get current tags
            content = self.get_content(content_id)
            if not content:
                raise ValueError(f"Content {content_id} not found")
            
            current_tags = set(content.get('tags', []))
            
            # Perform the requested operation
            if operation == 'set':
                new_tags = set(tags)
            elif operation == 'add':
                new_tags = current_tags | set(tags)
            elif operation == 'remove':
                new_tags = current_tags - set(tags)
            else:
                raise ValueError(f"Invalid operation: {operation}. Must be 'set', 'add', or 'remove'")
            
            # Update the content with new tags
            return self.update_metadata(content_id, {'tags': sorted(list(new_tags))})
            
        except Exception as e:
            raise ContentManagerError(f"Failed to update tags: {str(e)}")

