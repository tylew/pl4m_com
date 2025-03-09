"""
Configuration settings for PL4M utilities.

This module contains default configuration settings for bucket names, Firestore
collections, and content type definitions. Users can override these settings
by importing and modifying the values directly or by setting environment variables.
"""
from typing import Dict, Set, Any, List

# Default GCS bucket configuration - single bucket for all content
DEFAULT_GCS_BUCKET = "pl4m-public-content"

# Default Firestore collection 
DEFAULT_COLLECTION = "pl4m-content-library"

# Content type definitionss
# FOR BEST PERFORMANCE, REMEMBER TO UPDATE FIRESTORE INDEXES WHEN CHANGING THESE
CONTENT_TYPES = {
    "documents": {
        "valid_extensions": {'.pdf'},
        "required_metadata": {'title', 'description', 'tags'},
        "optional_metadata": {'author', 'page_count', 'created_date'},
        "default_content_type": "application/pdf",
        "collection": "tylers-platform-documents"
    },
    "images": {
        "valid_extensions": {'.jpg', '.jpeg', '.png', '.gif', '.webp'},
        "required_metadata": {'tags'},
        "optional_metadata": {'description', 'taken_at', 'created_date'},
        "mime_types": {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg', 
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp'
        },
        "collection": "tylers-platform-images"
    },
    "blog": {
        "valid_extensions": {'.md', '.markdown'},
        "required_metadata": {'title', 'description', 'tags', 'last_modified'},
        "optional_metadata": {'author', 'created_date'},
        "default_content_type": "text/markdown",
        "collection": "tylers-platform-blog"
    }
}

def get_bucket_name() -> str:
    """
    Get the configured bucket name.
    
    Returns:
        The configured bucket name
    """
    import os
    env_var = "PL4M_BUCKET"
    return os.environ.get(env_var, DEFAULT_GCS_BUCKET)

def get_content_type_config(content_type: str) -> Dict[str, Any]:
    """
    Get the configuration for a specific content type.
    
    Args:
        content_type: Type of content (e.g., 'documents', 'images', 'blog')
        
    Returns:
        Dictionary containing content type configuration
        
    Raises:
        ValueError: If content type is not defined
    """
    if content_type not in CONTENT_TYPES:
        raise ValueError(f"Undefined content type: {content_type}")
    return CONTENT_TYPES[content_type]

def get_collection_name(content_type: str) -> str:
    """
    Get the configured collection name for a given content type.
    
    Args:
        content_type: Type of content (e.g., 'documents', 'images', 'blog')
        
    Returns:
        The configured collection name
    """
    import os
    env_var = f"PL4M_COLLECTION_{content_type.upper()}"
    
    # Try environment variable first
    if env_var in os.environ:
        return os.environ[env_var]
    
    # Then try the content type config
    if content_type in CONTENT_TYPES and "collection" in CONTENT_TYPES[content_type]:
        return CONTENT_TYPES[content_type]["collection"]
    
    # Finally, use the default collection
    return DEFAULT_COLLECTION

def get_mime_type(content_type: str, filename: str) -> str:
    """
    Determine MIME type for a file based on its extension and content type.
    
    Args:
        content_type: Type of content (e.g., 'documents', 'images', 'blog')
        filename: Name of the file
        
    Returns:
        MIME type string
    """
    config = get_content_type_config(content_type)
    
    # Use content type's default if available
    if "default_content_type" in config:
        default_type = config["default_content_type"]
    else:
        default_type = "application/octet-stream"
    
    # If there's a mime_types mapping, use it
    if "mime_types" in config:
        ext = filename.lower().split('.')[-1]
        return config["mime_types"].get(ext, default_type)
    
    return default_type 