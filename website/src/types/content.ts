export interface ImageItem {
  blob_path: string;
  bucket: string;
  content_type: string;
  created_at: string;
  deleted_at: string | null;
  gcs_path: string;
  id: string;
  size_bytes: number;
  tags: string[];
  updated_at: string;
}

export interface ImageListResponse {
  items: ImageItem[];
  page: number;
  pages: number;
  per_page: number;
  total: number;
} 