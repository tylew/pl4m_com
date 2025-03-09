from pl4m_utils.content_manager import ContentManager, ContentManagerError
from pl4m_utils.metadata_manager import MetadataManager
from pl4m_utils.config import get_collection_name
from typing import Dict, Any, Optional
from datetime import datetime

class DocumentManager(ContentManager):
    """
    Manager for browser-viewable document content.
    
    This class extends ContentManager to handle PDF and other browser-viewable
    document types. It enforces document file types and manages document-specific
    metadata like title, author, and page count.
    """

    def __init__(self):
        """Initialize the document manager with PDF and other document settings."""
        super().__init__(
            collection=get_collection_name("documents"),
            content_type="documents",
            valid_extensions={'.pdf'}  # Can be extended for other document types
        )

    def create_document(self, gcs_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new document record with metadata and GCS path.
        
        Args:
            gcs_path: Full GCS path to the document file
            metadata: Document metadata including:
                     - title (required): Document title
                     - description (required): Document description
                     - tags (required): List or set of tags
                     - author (optional): Document author
                     - page_count (optional): Number of pages
                     
        Returns:
            Dictionary containing the complete document record
            
        Raises:
            ContentManagerError: If record creation fails
            ValueError: If metadata or path is invalid
        """
        try:
            self._validate_metadata(metadata)  # Base class validation

            # Additional document-specific validation
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
                raise ValueError(f"Document file does not exist: {gcs_path}")
            
            doc_data = metadata.copy()
            doc_data.update({
                'gcs_path': gcs_path,
                'bucket': bucket_name,
                'blob_path': blob_path,
                'size_bytes': blob.size,
                'content_type': blob.content_type or 'application/pdf'
            })
            
            return MetadataManager.create_document(self.COLLECTION, doc_data)
        except Exception as e:
            raise ContentManagerError(f"Failed to create document record: {str(e)}")

    def update_document_metadata(self, doc_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update document metadata.
        
        Args:
            doc_id: ID of the document record
            updates: Dictionary of fields to update, can include:
                    - title
                    - description
                    - tags
                    - author
                    - page_count
                    
        Returns:
            Updated document record
            
        Raises:
            ContentManagerError: If update fails
            ValueError: If updates contain invalid values
        """
        try:
            # Prevent updating critical fields
            protected_fields = {'gcs_path', 'bucket', 'blob_path', 'id', 'created_at', 'content_type'}
            invalid_fields = protected_fields.intersection(updates.keys())
            if invalid_fields:
                raise ValueError(f"Cannot update protected fields: {invalid_fields}")
            
            return MetadataManager.update_document(self.COLLECTION, doc_id, updates)
        except Exception as e:
            raise ContentManagerError(f"Failed to update document metadata: {str(e)}")

    def replace_document(self, doc_id: str, new_content: bytes) -> Dict[str, Any]:
        """
        Replace the content of an existing document.
        
        Args:
            doc_id: ID of the document record
            new_content: New document content as bytes
            
        Returns:
            Updated document record
            
        Raises:
            ContentManagerError: If replacement fails
            ValueError: If document not found
        """
        return self.update_content(doc_id, new_content, 'application/pdf')

    def upload_new_document(self, filename: str, content: bytes, metadata: Dict[str, Any], 
                            date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Upload a new document with content and metadata in one operation.
        
        Args:
            filename: Name of the document file
            content: Document content as bytes
            metadata: Document metadata
            date: Optional date for path generation (defaults to today)
            
        Returns:
            Complete document record
        """
        try:
            self._validate_extension(filename)
            self._validate_metadata(metadata)
            
            # Additional document-specific validation
            required_fields = {'title', 'description'}
            missing_fields = required_fields - metadata.keys()
            if missing_fields:
                raise ValueError(f"Missing required metadata fields: {missing_fields}")
            
            # Generate path and upload file
            file_path = self._generate_file_path(filename, date)
            bucket = self.storage_client.bucket(self.BUCKET)
            blob = bucket.blob(file_path)
            
            content_type = 'application/pdf'
            blob.upload_from_string(content, content_type=content_type)
            
            # Create metadata record
            gcs_path = f"gs://{self.BUCKET}/{file_path}"
            doc_data = metadata.copy()
            doc_data.update({
                'gcs_path': gcs_path,
                'bucket': self.BUCKET,
                'blob_path': file_path,
                'size_bytes': len(content),
                'content_type': content_type
            })
            
            return MetadataManager.create_document(self.COLLECTION, doc_data)
        except Exception as e:
            raise ContentManagerError(f"Failed to upload new document: {str(e)}") 