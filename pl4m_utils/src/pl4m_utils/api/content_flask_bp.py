"""
Flask API interface for PL4M utilities content management system.

This module provides REST endpoints for interacting with the content management system,
including uploading, retrieving, updating, and deleting content of various types.
"""

from flask import Blueprint, request, jsonify, send_file
from datetime import datetime, timedelta
import io
import json
from typing import Dict, Any, Optional, List
from pl4m_utils import ContentManager, ContentManagerError
from pl4m_utils.config import CONTENT_TYPES

# Create Blueprint instead of Flask app
bp = Blueprint('content', __name__)

def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse date string into datetime object."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        return None

@bp.errorhandler(ContentManagerError)
def handle_content_error(error):
    """Handle content management errors."""
    return jsonify({
        'error': str(error),
        'type': 'ContentManagerError'
    }), 400

@bp.errorhandler(ValueError)
def handle_value_error(error):
    """Handle validation errors."""
    return jsonify({
        'error': str(error),
        'type': 'ValueError'
    }), 400

@bp.route('/api/content/types', methods=['GET'])
def list_content_types():
    """List available content types and their configurations."""
    return jsonify({
        'content_types': {
            type_name: {
                'valid_extensions': list(config['valid_extensions']),
                'required_metadata': list(config['required_metadata']),
                'optional_metadata': list(config.get('optional_metadata', [])),
            }
            for type_name, config in CONTENT_TYPES.items()
        }
    })

@bp.route('/api/content/<content_type>', methods=['POST'])
def upload_content(content_type: str):
    """
    Upload new content.
    
    Expected form data:
    - file: The content file
    - metadata: JSON string of metadata
    - creation_date: (optional) ISO format date string
    - path_date: (optional) ISO format date for path generation
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'No filename provided'}), 400

    try:
        metadata = json.loads(request.form.get('metadata', '{}'))
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid metadata JSON'}), 400

    creation_date = parse_date(request.form.get('creation_date'))
    path_date = parse_date(request.form.get('path_date'))

    manager = ContentManager(content_type=content_type)
    
    result = manager.upload_new_content(
        filename=file.filename,
        content=file.read(),
        metadata=metadata,
        date=path_date,
        creation_date=creation_date
    )
    
    return jsonify(result), 201

@bp.route('/api/content/<content_type>/<content_id>', methods=['GET'])
def get_content(content_type: str, content_id: str):
    """
    Retrieve content and metadata.
    
    Query parameters:
    - metadata_only: If 'true', only return metadata without content
    """
    manager = ContentManager(content_type=content_type)
    
    # Get the content metadata
    metadata = manager.get_content(content_id)
    if not metadata:
        return jsonify({'error': 'Content not found'}), 404

    # Return only metadata if requested
    if request.args.get('metadata_only') == 'true':
        return jsonify(metadata)

    # Get the actual content from GCS
    try:
        bucket = manager.storage_client.bucket(metadata['bucket'])
        blob = bucket.blob(metadata['blob_path'])
        content = blob.download_as_bytes()
            
        # Create in-memory file
        file_obj = io.BytesIO(content)
        
        return send_file(
            file_obj,
            mimetype=metadata.get('content_type', 'application/octet-stream'),
            as_attachment=True,
            download_name=metadata.get('blob_path', '').split('/')[-1]
        )
    except Exception as e:
        return jsonify({'error': f'Error retrieving content: {str(e)}'}), 500

@bp.route('/api/content/<content_type>/<content_id>', methods=['PATCH'])
def update_content(content_type: str, content_id: str):
    """
    Update content metadata and/or content.
    
    Expected JSON body:
    {
        "metadata": {field: value, ...},  # Optional
        "content": base64_encoded_content  # Optional
    }
    """
    manager = ContentManager(content_type=content_type)
    
    # Verify content exists
    if not manager.get_content(content_id):
        return jsonify({'error': 'Content not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No update data provided'}), 400

    result = {}

    # Update metadata if provided
    if 'metadata' in data:
        try:
            result['metadata'] = manager.update_metadata(content_id, data['metadata'])
        except Exception as e:
            return jsonify({'error': f'Error updating metadata: {str(e)}'}), 400

    # Update content if provided
    if 'content' in data:
        try:
            import base64
            content = base64.b64decode(data['content'])
            # result['content'] = 
            manager.update_content(content_id, content)
        except Exception as e:
            return jsonify({'error': f'Error updating content: {str(e)}'}), 400

    return jsonify(result)

@bp.route('/api/content/<content_type>/<content_id>', methods=['DELETE'])
def delete_content(content_type: str, content_id: str):
    """
    Delete content.
    
    Query parameters:
    - hard_delete: If 'true', permanently delete content
    """
    manager = ContentManager(content_type=content_type)
    
    # Verify content exists
    if not manager.get_content(content_id):
        return jsonify({'error': 'Content not found'}), 404

    hard_delete = request.args.get('hard_delete') == 'true'
    
    try:
        result = manager.delete_content(content_id, hard_delete=hard_delete)
        return jsonify({'success': result})
    except Exception as e:
        return jsonify({'error': f'Error deleting content: {str(e)}'}), 500

@bp.route('/api/content/<content_type>/<content_id>/restore', methods=['POST'])
def restore_content(content_type: str, content_id: str):
    """Restore soft-deleted content."""
    manager = ContentManager(content_type=content_type)
    
    try:
        result = manager.restore_content(content_id)
        return jsonify({'success': result})
    except Exception as e:
        return jsonify({'error': f'Error restoring content: {str(e)}'}), 500

@bp.route('/api/content/<content_type>/list', methods=['GET'])
def list_content(content_type: str):
    """
    Get paginated list of content with optional filtering.
    
    Query parameters:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20, max: 100)
    - tags: Comma-separated list of tags to filter by
    - from_date: ISO date to filter from (inclusive)
    - to_date: ISO date to filter to (inclusive)
    - sort_by: Field to sort by (default: 'created_at')
    - sort_order: 'asc' or 'desc' (default: 'desc')
    """
    try:
        # Parse pagination parameters
        page = max(1, int(request.args.get('page', 1)))
        per_page = min(100, max(1, int(request.args.get('per_page', 20))))
        
        # Parse filter parameters
        tags = request.args.get('tags', '').split(',') if request.args.get('tags') else None
        from_date = parse_date(request.args.get('from_date'))
        to_date = parse_date(request.args.get('to_date'))
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Build filter conditions
        filters = []
        
        # Tag filter
        if tags:
            filters.append(('tags', 'array_contains_any', [t.strip() for t in tags if t.strip()]))
        
        # Date range filters
        if from_date:
            filters.append(('created_at', '>=', from_date))
        if to_date:
            filters.append(('created_at', '<=', to_date))
        
        # Create manager and get paginated results
        manager = ContentManager(content_type=content_type)
        results = manager.list_content(
            page=page,
            per_page=per_page,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return jsonify(results)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Error listing content: {str(e)}'}), 500

@bp.route('/api/content/tags', methods=['GET'])
def get_all_content_tags():
    """
    Get all unique tags across all content types.
    
    Query parameters:
    - include_deleted: If 'true', include tags from soft-deleted content
    
    Returns:
        JSON object with tags grouped by content type and a combined list
    """
    try:
        include_deleted = request.args.get('include_deleted') == 'true'
        result = {
            'by_type': {},
            'all_tags': set()
        }
        
        # Iterate through defined content types
        for content_type in CONTENT_TYPES.keys():
            manager = ContentManager(content_type=content_type)
            type_tags = manager.get_available_tags()
            
            result['by_type'][content_type] = type_tags
            result['all_tags'].update(type_tags)
        
        # Convert set to sorted list for JSON serialization
        result['all_tags'] = sorted(list(result['all_tags']))
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Error retrieving tags: {str(e)}'}), 500

@bp.route('/api/content/<content_type>/tags', methods=['GET'])
def get_content_type_tags(content_type: str):
    """
    Get all unique tags for a specific content type.
    
    Query parameters:
    - include_deleted: If 'true', include tags from soft-deleted content
    
    Returns:
        JSON object with list of tags
    """
    try:
        include_deleted = request.args.get('include_deleted') == 'true'
        
        manager = ContentManager(content_type=content_type)
        tags = manager.get_available_tags()
        
        return jsonify({
            'content_type': content_type,
            'tags': tags
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Error retrieving tags: {str(e)}'}), 500 