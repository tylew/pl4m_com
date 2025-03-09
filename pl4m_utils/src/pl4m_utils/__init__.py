from pl4m_utils.metadata_manager import MetadataManager, MetadataManagerError
from pl4m_utils.content_manager import ContentManager, ContentManagerError
from pl4m_utils.config import (
    get_bucket_name, get_content_type_config, 
    get_collection_name, get_mime_type, CONTENT_TYPES
)

# Legacy class aliases for backward compatibility
class DocumentManager(ContentManager):
    def __init__(self):
        super().__init__(content_type="documents")

class ImageManager(ContentManager):
    def __init__(self):
        super().__init__(content_type="images")

class BlogManager(ContentManager):
    def __init__(self):
        super().__init__(content_type="blog")