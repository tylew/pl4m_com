from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from typing import Optional, List, Dict, Any
from datetime import datetime

class MetadataManagerError(Exception):
    """Custom exception for MetadataManager-related errors."""
    pass

class MetadataManager:
    """
    A utility class for managing Firestore document operations.
    
    Key methods:
    - create_document(collection, data, custom_timestamps=None) -> dict
    - read_document(collection, document_id, include_deleted=False) -> Optional[dict]
    - update_document(collection, document_id, updates) -> dict
    - list_documents(collection, include_deleted=False, limit=None, order_by='created_at', 
                    descending=True, filters=None, page=None, per_page=None) -> dict
    - soft_delete(collection, document_id) -> bool
    - restore_document(collection, document_id) -> bool
    - hard_delete_document(collection, document_id) -> bool

    All documents automatically include:
    - id: str (document ID)
    - created_at: datetime
    - updated_at: datetime 
    - deleted_at: Optional[datetime]

    Raises MetadataManagerError for operation failures.
    """

    db = firestore.Client()

    @staticmethod
    def create_document(collection: str, data: Dict[str, Any], 
                        custom_timestamps: Optional[Dict[str, datetime]] = None) -> Dict[str, Any]:
        """
        Creates a new document in Firestore with automatic timestamp.
        
        Args:
            collection: Name of the Firestore collection
            data: Document data to store
            custom_timestamps: Optional dict with custom timestamp values
                               (e.g., {'created_at': custom_datetime})
            
        Returns:
            Dictionary containing the document data and its ID
            
        Raises:
            ValueError: If collection is empty or data is invalid
            MetadataManagerError: If database operation fails
        """
        if not collection or not isinstance(data, dict):
            raise ValueError("Invalid collection name or data format")
            
        try:
            doc_ref = MetadataManager.db.collection(collection).document()
            doc_data = data.copy()
            
            # Set default timestamps
            now = datetime.utcnow()
            timestamp_data = {
                'id': doc_ref.id,  # Include document ID in the data
                'created_at': now,
                'updated_at': now,
                'deleted_at': None
            }
            
            # Override with custom timestamps if provided
            if custom_timestamps:
                for key, value in custom_timestamps.items():
                    if key in timestamp_data:
                        timestamp_data[key] = value
            
            doc_data.update(timestamp_data)
            doc_ref.set(doc_data)
            
            # Store with server timestamp in Firestore
            # firestore_data = doc_data.copy()
            # firestore_data['created_at'] = firestore.SERVER_TIMESTAMP
            # firestore_data['updated_at'] = firestore.SERVER_TIMESTAMP
            # doc_ref.set(firestore_data)
            
            # Return JSON serializable data
            return doc_data
        except Exception as e:
            raise MetadataManagerError(f"Failed to create document: {str(e)}")

    @staticmethod
    def read_document(collection: str, document_id: str, include_deleted: bool = False) -> Optional[Dict[str, Any]]:
        """
        Retrieves a document by ID, with option to include soft-deleted documents.
        
        Args:
            collection: Name of the Firestore collection
            document_id: Document's unique identifier
            include_deleted: If True, returns document even if soft-deleted
            
        Returns:
            Document data dictionary or None if not found or soft-deleted
            
        Raises:
            ValueError: If collection or document_id is invalid
            MetadataManagerError: If database operation fails
        """
        if not collection or not document_id:
            raise ValueError("Collection and document_id must not be empty")
            
        try:
            doc = MetadataManager.db.collection(collection).document(document_id).get()
            if not doc.exists:
                return None  # Return None instead of raising ValueError
                
            data = doc.to_dict()
            if not include_deleted and data.get('deleted_at'):
                return None
            return data
        except Exception as e:
            raise MetadataManagerError(f"Failed to read document: {str(e)}")

    @staticmethod
    def update_document(collection: str, document_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates specific fields in an existing document.
        
        Args:
            collection: Name of the Firestore collection
            document_id: Document's unique identifier
            updates: Dictionary of fields and values to update
            
        Returns:
            Complete updated document data
            
        Raises:
            ValueError: If document doesn't exist or is soft-deleted
            MetadataManagerError: If database operation fails
        """
        if not collection or not document_id or not updates:
            raise ValueError("Missing required parameters")
            
        try:
            doc_ref = MetadataManager.db.collection(collection).document(document_id)
            current = doc_ref.get()
            
            if not current.exists:
                raise ValueError(f"Document {document_id} not found")
                
            if current.to_dict().get('deleted_at'):
                raise ValueError(f"Cannot update deleted document {document_id}")
                
            updates['updated_at'] = firestore.SERVER_TIMESTAMP
            doc_ref.update(updates)
            
            return MetadataManager.read_document(collection, document_id)
        except Exception as e:
            raise MetadataManagerError(f"Failed to update document: {str(e)}")

    @staticmethod
    def list_documents(
        collection: str,
        include_deleted: bool = False,
        limit: Optional[int] = None,
        order_by: str = 'created_at',
        descending: bool = True,
        filters: Optional[List[Dict[str, Any]]] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Retrieves a filtered and ordered list of documents.
        
        Args:
            collection: Name of the Firestore collection
            include_deleted: If True, includes soft-deleted documents
            limit: Maximum number of documents to return
            order_by: Field to sort by
            descending: Sort order direction
            filters: List of filter dictionaries with format:
                    [
                        {
                            "field": Field name to filter on,
                            "op": Operator for comparison ("==", ">=", "array_contains_any" etc),
                            "value": Value to compare against
                        },
                        ...
                    ]
            page: Page number for pagination (starting from 1)
            per_page: Number of items per page
            
        Returns:
            Dictionary containing:
                items: List of document dictionaries
                total: Total number of matching items
                page: Current page number (if pagination used)
                per_page: Items per page (if pagination used)
                pages: Total number of pages (if pagination used)
            
        Raises:
            MetadataManagerError: If database operation fails
        """
        try:
            query = MetadataManager.db.collection(collection)
            
            if not include_deleted:
                query = query.where(filter=FieldFilter('deleted_at', '==', None))

            # Apply any additional filters
            if filters:
                for f in filters:
                    query = query.where(filter=FieldFilter(f['field'], f['op'], f['value']))
                
            query = query.order_by(order_by, direction=firestore.Query.DESCENDING if descending else firestore.Query.ASCENDING)
            
            # Get all matching documents
            all_docs = [doc.to_dict() for doc in query.stream()]
            total_items = len(all_docs)

            # Apply pagination if specified
            if page is not None and per_page is not None:
                start_idx = (page - 1) * per_page
                end_idx = start_idx + per_page
                items = all_docs[start_idx:end_idx]
                total_pages = (total_items + per_page - 1) // per_page
                
                return {
                    'items': items,
                    'total': total_items,
                    'page': page,
                    'per_page': per_page,
                    'pages': total_pages
                }
            
            # Apply limit if specified
            if limit:
                all_docs = all_docs[:limit]
                
            return {
                'items': all_docs,
                'total': total_items
            }
            
        except Exception as e:
            raise MetadataManagerError(f"Failed to list documents: {str(e)}")

    @staticmethod
    def soft_delete(collection: str, document_id: str) -> bool:
        """
        Marks a document as deleted without removing it.
        
        Args:
            collection: Name of the Firestore collection
            document_id: Document's unique identifier
            
        Returns:
            True if successful
            
        Raises:
            ValueError: If document is already deleted
            MetadataManagerError: If database operation fails
        """
        try:
            doc_ref = MetadataManager.db.collection(collection).document(document_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                raise ValueError(f"Document {document_id} not found")
                
            if doc.to_dict().get('deleted_at'):
                raise ValueError(f"Document {document_id} is already deleted")
                
            doc_ref.update({
                'deleted_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            return True
        except Exception as e:
            raise MetadataManagerError(f"Failed to soft-delete document: {str(e)}")

    @staticmethod
    def restore_document(collection: str, document_id: str) -> bool:
        """
        Restores a soft-deleted document.
        
        Args:
            collection: Name of the Firestore collection
            document_id: Document's unique identifier
            
        Returns:
            True if successful
            
        Raises:
            ValueError: If document isn't deleted or doesn't exist
            MetadataManagerError: If database operation fails
        """
        try:
            doc_ref = MetadataManager.db.collection(collection).document(document_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                raise ValueError(f"Document {document_id} not found")
                
            if not doc.to_dict().get('deleted_at'):
                raise ValueError(f"Document {document_id} is not deleted")
                
            doc_ref.update({
                'deleted_at': None,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            return True
        except Exception as e:
            raise MetadataManagerError(f"Failed to restore document: {str(e)}")

    @staticmethod
    def hard_delete_document(collection: str, document_id: str) -> bool:
        """
        Permanently deletes a document from Firestore.
        
        Args:
            collection (str): The name of the Firestore collection.
            document_id (str): The unique identifier of the document.

        Returns:
            bool: True if the deletion succeeds, False otherwise.
        """
        try:
            MetadataManager.db.collection(collection).document(document_id).delete()
            return True
        except Exception as e:
            raise ValueError(f"Error permanently deleting document '{document_id}' from '{collection}': {e}")

    @staticmethod
    def get_distinct_tags(collection: str, include_deleted: bool = False) -> List[str]:
        """
        Retrieves a list of all unique tags from documents in the collection.
        
        Args:
            collection: Name of the Firestore collection
            include_deleted: If True, includes tags from soft-deleted documents
            
        Returns:
            List of unique tags sorted alphabetically
            
        Raises:
            MetadataManagerError: If database operation fails
        """
        try:
            query = MetadataManager.db.collection(collection)
            
            # Exclude soft-deleted documents unless specified
            if not include_deleted:
                query = query.where(filter=FieldFilter('deleted_at', '==', None))
            
            # Get only the tags field from all documents
            docs = query.select(['tags']).stream()
            
            # Collect all unique tags
            unique_tags = set()
            for doc in docs:
                tags = doc.to_dict().get('tags', [])
                if isinstance(tags, (list, set)):
                    unique_tags.update(tags)
            
            # Return sorted list of tags
            return sorted(list(unique_tags))
            
        except Exception as e:
            raise MetadataManagerError(f"Failed to get distinct tags: {str(e)}")

