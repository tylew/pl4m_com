import pytest
from google.cloud import firestore
from pl4m_utils.metadata_manager import MetadataManager  # Adjust import based on your module structure
import time

# @pytest.fixture(scope="module")
# def firestore_client():
#     """Provides a Firestore client instance for testing."""
#     return firestore.Client()

@pytest.fixture(scope="module")
def metadata_manager():
    """Provides an instance of MetadataManager."""
    return MetadataManager()

@pytest.fixture
def test_collection():
    """Returns a Firestore collection name for testing."""
    return "test_metadata"

@pytest.fixture
def test_document():
    """Returns sample test data."""
    return {
        "name": "Test Document",
        "type": "example",
        "value": 42
    }

def test_create_document(metadata_manager, test_collection, test_document):
    """Test creating a Firestore document."""
    created_doc = metadata_manager.create_document(test_collection, test_document)
    assert created_doc is not None
    assert created_doc["name"] == test_document["name"]
    assert "id" in created_doc

def test_read_document(metadata_manager, test_collection, test_document):
    """Test reading a Firestore document."""
    created_doc = metadata_manager.create_document(test_collection, test_document)
    doc_id = created_doc["id"]
    
    retrieved_doc = metadata_manager.read_document(test_collection, doc_id)
    assert retrieved_doc is not None
    assert retrieved_doc["name"] == test_document["name"]

def test_update_document(metadata_manager, test_collection, test_document):
    """Test updating a Firestore document."""
    created_doc = metadata_manager.create_document(test_collection, test_document)
    doc_id = created_doc["id"]
    
    updates = {"value": 100}
    updated_doc = metadata_manager.update_document(test_collection, doc_id, updates)
    assert updated_doc is not None
    assert updated_doc["value"] == 100

def test_soft_delete_document(metadata_manager, test_collection, test_document):
    """Test soft deleting a document."""
    created_doc = metadata_manager.create_document(test_collection, test_document)
    doc_id = created_doc["id"]
    
    assert metadata_manager.soft_delete(test_collection, doc_id) is True
    deleted_doc = metadata_manager.read_document(test_collection, doc_id, include_deleted=True)
    assert deleted_doc is not None
    assert deleted_doc.get("deleted_at") is not None

def test_restore_document(metadata_manager, test_collection, test_document):
    """Test restoring a soft-deleted document."""
    created_doc = metadata_manager.create_document(test_collection, test_document)
    doc_id = created_doc["id"]
    
    metadata_manager.soft_delete(test_collection, doc_id)
    assert metadata_manager.restore_document(test_collection, doc_id) is True
    restored_doc = metadata_manager.read_document(test_collection, doc_id)
    assert restored_doc["deleted_at"] is None

def test_list_documents(metadata_manager, test_collection):
    """Test listing documents."""
    docs = metadata_manager.list_documents(test_collection)
    assert isinstance(docs, list)

def test_hard_delete_document(metadata_manager, test_collection, test_document):
    """Test permanently deleting a document."""
    created_doc = metadata_manager.create_document(test_collection, test_document)
    doc_id = created_doc["id"]
    
    assert metadata_manager.hard_delete_document(test_collection, doc_id) is True
    assert metadata_manager.read_document(test_collection, doc_id) is None