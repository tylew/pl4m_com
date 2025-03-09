#!/usr/bin/env python3
"""
Test content generator for PL4M utilities.

This script creates various test content items using the ContentManager to populate
the storage bucket and Firestore collections with sample data. It demonstrates the 
different content types and various features of the content management system.
"""

import os
import sys
import argparse
import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List

from pl4m_utils import (
    ContentManager, DocumentManager, ImageManager, BlogManager
)

# Sample content data
SAMPLE_TEXT = """
This is sample text content for testing purposes.
It contains multiple lines and can be used to simulate
real content in the system.

Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
"""

# Sample PDF content - just a minimal valid PDF file
SAMPLE_PDF = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000010 00000 n\n0000000053 00000 n\n0000000102 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF"

# Sample JPEG content - minimal header that appears to be a valid JPEG
SAMPLE_JPEG = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x03\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xff\xd9'

def generate_random_tags(min_count: int = 2, max_count: int = 5) -> List[str]:
    """Generate a random list of tags."""
    all_tags = [
        "test", "sample", "demo", "example", "generated", "content", 
        "pl4m", "automated", "tag", "metadata", "firestore", "storage"
    ]
    count = random.randint(min_count, min(max_count, len(all_tags)))
    return random.sample(all_tags, count)

def generate_random_date(days_back: int = 365) -> datetime:
    """Generate a random date within the specified number of days back from now."""
    max_seconds_back = days_back * 24 * 60 * 60
    random_seconds = random.randint(0, max_seconds_back)
    return datetime.utcnow() - timedelta(seconds=random_seconds)

def create_test_documents(count: int = 3, use_specific_dates: bool = True) -> List[str]:
    """Create test PDF documents."""
    document_ids = []
    document_manager = DocumentManager()
    
    print(f"Creating {count} test documents...")
    
    for i in range(count):
        # Generate unique filename
        filename = f"test_document_{uuid.uuid4().hex[:8]}.pdf"
        
        # Create document metadata
        metadata = {
            "title": f"Test Document {i+1}",
            "description": f"This is a test document #{i+1} created for testing purposes",
            "tags": generate_random_tags(),
            "author": "Test Script"
        }
        
        # Optionally use a specific creation date
        creation_date = None
        if use_specific_dates:
            creation_date = generate_random_date()
            print(f"  - Using custom creation date: {creation_date}")
        
        try:
            # Upload document
            result = document_manager.upload_new_content(
                filename=filename,
                content=SAMPLE_PDF,
                metadata=metadata,
                creation_date=creation_date
            )
            
            document_ids.append(result['id'])
            print(f"  - Created document {i+1}: {result['id']} - {metadata['title']}")
            
        except Exception as e:
            print(f"  - Error creating document {i+1}: {str(e)}")
    
    return document_ids

def create_test_images(count: int = 3) -> List[str]:
    """Create test JPEG images."""
    image_ids = []
    image_manager = ImageManager()
    
    print(f"Creating {count} test images...")
    
    for i in range(count):
        # Generate unique filename with different extensions to test MIME type mapping
        extensions = ['.jpg', '.png', '.gif', '.webp']
        ext = random.choice(extensions)
        filename = f"test_image_{uuid.uuid4().hex[:8]}{ext}"
        
        # Create image metadata
        metadata = {
            "tags": generate_random_tags(),
            "description": f"Test image #{i+1} with {ext} extension",
            "taken_at": generate_random_date(30)  # Random date in the last month
        }
        
        try:
            # Upload image - using the same JPEG sample data regardless of extension
            # just to demonstrate the capability
            result = image_manager.upload_new_content(
                filename=filename,
                content=SAMPLE_JPEG,
                metadata=metadata
            )
            
            image_ids.append(result['id'])
            print(f"  - Created image {i+1}: {result['id']} - {filename}")
            
        except Exception as e:
            print(f"  - Error creating image {i+1}: {str(e)}")
    
    return image_ids

def create_test_blog_posts(count: int = 3) -> List[str]:
    """Create test markdown blog posts."""
    post_ids = []
    
    # Use the generic ContentManager directly to show it works the same
    blog_manager = ContentManager(content_type="blog")
    
    print(f"Creating {count} test blog posts...")
    
    for i in range(count):
        # Generate unique filename
        filename = f"test_post_{uuid.uuid4().hex[:8]}.md"
        
        # Create blog post metadata
        metadata = {
            "title": f"Test Blog Post {i+1}",
            "description": f"This is a test blog post #{i+1}",
            "tags": generate_random_tags(),
            "author": "Test Script",
            "publish_date": generate_random_date(60)  # Random date in the last 2 months
        }
        
        # Create blog post content
        content = f"""# {metadata['title']}

{metadata['description']}

{SAMPLE_TEXT}

## Tags

{', '.join(metadata['tags'])}

_Posted by {metadata['author']} on {metadata['publish_date'].strftime('%Y-%m-%d')}_
"""
        
        try:
            # Upload blog post
            result = blog_manager.upload_new_content(
                filename=filename,
                content=content,
                metadata=metadata
            )
            
            post_ids.append(result['id'])
            print(f"  - Created blog post {i+1}: {result['id']} - {metadata['title']}")
            
        except Exception as e:
            print(f"  - Error creating blog post {i+1}: {str(e)}")
    
    return post_ids

def update_test_content(content_ids: List[str]) -> None:
    """Update some of the test content to demonstrate update methods."""
    if not content_ids:
        print("No content IDs provided for update testing")
        return
    
    # Pick a random content ID to update
    content_id = random.choice(content_ids)
    
    # Create a generic content manager (we could also determine the type and use a specific manager)
    content_manager = ContentManager(content_type="documents")  # Type doesn't matter for reading/updating
    
    print(f"Updating test content: {content_id}")
    
    try:
        # Get the content
        content = content_manager.get_content(content_id)
        if not content:
            print(f"  - Content not found: {content_id}")
            return
        
        # Determine the type based on content_type or collection
        content_type = None
        if 'content_type' in content:
            if 'markdown' in content['content_type']:
                content_type = "blog"
            elif 'pdf' in content['content_type']:
                content_type = "documents"
            elif 'image/' in content['content_type']:
                content_type = "images"
        
        if not content_type:
            print(f"  - Could not determine content type for: {content_id}")
            return
        
        # Create the appropriate manager
        manager = ContentManager(content_type=content_type)
        
        # Update the metadata
        update_data = {
            "tags": generate_random_tags(),
            "description": f"Updated description: {datetime.utcnow().isoformat()}"
        }
        
        result = manager.update_metadata(content_id, update_data)
        print(f"  - Updated metadata for {content_id}: {update_data['description']}")
        
        # If it's a blog post, also update the content
        if content_type == "blog":
            new_content = f"""# Updated Blog Post

This content was updated on {datetime.utcnow().isoformat()}

{SAMPLE_TEXT}

## Updated Tags

{', '.join(update_data['tags'])}
"""
            manager.update_content(content_id, new_content)
            print(f"  - Updated content for blog post: {content_id}")
        
    except Exception as e:
        print(f"  - Error updating content {content_id}: {str(e)}")

def main():
    """Main function to run the test content generator."""
    parser = argparse.ArgumentParser(description='Generate test content for PL4M utilities')
    parser.add_argument('--documents', type=int, default=2, help='Number of test documents to create')
    parser.add_argument('--images', type=int, default=2, help='Number of test images to create')
    parser.add_argument('--blog-posts', type=int, default=2, help='Number of test blog posts to create')
    parser.add_argument('--no-updates', action='store_true', help='Skip updating content')
    
    args = parser.parse_args()
    
    print("PL4M Test Content Generator")
    print("==========================")
    
    # Create test content
    doc_ids = create_test_documents(args.documents)
    image_ids = create_test_images(args.images)
    post_ids = create_test_blog_posts(args.blog_posts)
    
    # Combine all content IDs
    all_content_ids = doc_ids + image_ids + post_ids
    
    # Update some content if requested
    if not args.no_updates and all_content_ids:
        update_test_content(all_content_ids)
    
    print("\nTest Content Generation Summary:")
    print(f"  - Documents created: {len(doc_ids)}")
    print(f"  - Images created: {len(image_ids)}")
    print(f"  - Blog posts created: {len(post_ids)}")
    print(f"  - Total items: {len(all_content_ids)}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 