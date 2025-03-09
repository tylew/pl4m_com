# PL4M Utilities Content Management System Overview

## Architecture Summary

The PL4M utilities package implements a unified content management system for Google Cloud Storage (GCS) and Firestore, with the following key features:

- **Centralized Configuration**: A single config module defines all settings and content types
- **Single Driver Design**: A unified `ContentManager` class handles various content types
- **Date-Based Storage**: Content is automatically organized in folders by date and type
- **Metadata Management**: Automatic tracking of creation/modification dates and content attributes
- **Compatibility Layers**: Legacy class aliases preserve backward compatibility

## Core Components

### 1. Configuration System (`config.py`)

- Defines content types, required metadata, and allowed file extensions
- Sets default bucket name (`pl4m-public-content`) and collection (`pl4m-content-library`)
- Provides helper functions to get bucket names, collection names, and MIME types
- Supports environment variable overrides like `PL4M_BUCKET` and `PL4M_COLLECTION_*`

### 2. Metadata Manager (`metadata_manager.py`) 

- Handles all Firestore interactions (CRUD operations)
- Provides automatic timestamping for document creation/updates
- Implements soft delete and restore capabilities
- Supports custom timestamps for creation dates

### 3. Content Manager (`content_manager.py`)

- Central class for managing all content types
- Handles file uploads, updates, and retrievals from GCS
- Validates metadata against required fields
- Generates structured paths for content storage
- Automatically tracks last modified dates when `last_modified` is in the configuration required metadata
- Provides both high-level and content-type-specific operations

### 4. Legacy Support Classes (in `__init__.py`)

- `DocumentManager`: For PDF documents
- `ImageManager`: For image formats
- `BlogManager`: For markdown blog content

## Key Workflows

### Content Creation

```python
# Using unified class with type parameter
manager = ContentManager(content_type="documents")
result = manager.upload_new_content(
    filename="example.pdf",
    content=pdf_bytes,
    metadata={
        "title": "Example Document",
        "description": "A sample document",
        "tags": ["sample", "document"]
    },
    date=some_date,  # Optional: Controls storage path
    creation_date=some_date  # Optional: Sets document creation timestamp
)

# Or using legacy classes
doc_manager = DocumentManager()
result = doc_manager.upload_new_content(...)
```

### Content Retrieval and Update

```python
# Get content by ID
content = manager.get_content(content_id)

# Update metadata
manager.update_metadata(content_id, {"tags": ["new", "tags"]})

# Update content
manager.update_content(content_id, new_content_bytes)
```

### Content Management

```python
# Soft delete (can be restored)
manager.delete_content(content_id)

# Hard delete (permanent)
manager.delete_content(content_id, hard_delete=True)

# Restore soft-deleted content
manager.restore_content(content_id)
```

## Special Features

1. **Automatic Date-Based Paths**: Content is stored in `{YYYY}/{MM}/{DD}/{content_type}/{filename}`
2. **Custom Creation Dates**: Creation timestamps can be overridden for historical content
3. **Automatic Last-Modified**: The system tracks last-modified dates automatically when `last_modified` is in the configuration required metadata
4. **MIME Type Detection**: File types are automatically detected based on extensions
5. **Content Type Validation**: Files are validated against allowed extensions
6. **Metadata Validation**: Required fields are enforced for each content type

The system is designed to be extendable - new content types can be added simply by updating the configuration file, without creating new manager classes.
