from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from typing import Optional, List, Dict, Any
from datetime import datetime

class MetadataManagerError(Exception):
    """Custom exception for MetadataManager-related errors."""
    pass

class MetadataManager:
    """
    A static utility class for managing Firestore document operations.
    
    This class provides a comprehensive set of methods for CRUD operations on Firestore
    documents, including soft deletion and restoration capabilities. All methods are
    static as this class is not meant to be instantiated.
    """

    db = firestore.Client()

    @staticmethod
    def create_document(collection: str, data: Dict[str, Any]) -> str:
        """
        Creates a new document in Firestore with automatic timestamp.
        
        Args:
            collection: Name of the Firestore collection
            data: Document data to store
            
        Returns:
            The ID of the created document
            
        Raises:
            ValueError: If collection is empty or data is invalid
            MetadataManagerError: If database operation fails
        """
        if not collection or not isinstance(data, dict):
            raise ValueError("Invalid collection name or data format")
            
        try:
            doc_ref = MetadataManager.db.collection(collection).document()
            data.update({
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP,
                'deleted_at': None
            })
            doc_ref.set(data)
            return doc_ref.id
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
            Document data dictionary or None if not found
            
        Raises:
            ValueError: If collection or document_id is invalid
            MetadataManagerError: If database operation fails
        """
        if not collection or not document_id:
            raise ValueError("Collection and document_id must not be empty")
            
        try:
            doc = MetadataManager.db.collection(collection).document(document_id).get()
            if not doc.exists:
                raise ValueError(f"Document {document_id} not found")
                
            data = doc.to_dict()
            if not include_deleted and data.get('deleted_at'):
                raise ValueError(f"Document {document_id} is soft-deleted")
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
        descending: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieves a filtered and ordered list of documents.
        
        Args:
            collection: Name of the Firestore collection
            include_deleted: If True, includes soft-deleted documents
            limit: Maximum number of documents to return
            order_by: Field to sort by
            descending: Sort order direction
            
        Returns:
            List of document dictionaries
            
        Raises:
            MetadataManagerError: If database operation fails
        """
        try:
            query = MetadataManager.db.collection(collection)
            
            if not include_deleted:
                query = query.where(filter=FieldFilter('deleted_at', '==', None))
                
            query = query.order_by(order_by, direction=firestore.Query.DESCENDING if descending else firestore.Query.ASCENDING)
            
            if limit:
                query = query.limit(limit)
                
            return [doc.to_dict() for doc in query.stream()]
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

