resource "google_storage_bucket" "blog_md" {
  name          = "${var.project_id}-blog-md"
  location      = var.region
  storage_class = var.storage_class
  uniform_bucket_level_access = true
}

resource "google_storage_bucket" "image_gallery" {
  name          = "${var.project_id}-images"
  location      = var.region
  storage_class = var.storage_class
  uniform_bucket_level_access = true
}

resource "google_storage_bucket" "pdf_archive" {
  name          = "${var.project_id}-pdf-archive"
  location      = var.region
  storage_class = var.storage_class
  uniform_bucket_level_access = true
}

// Add public access for images bucket
resource "google_storage_bucket_iam_member" "images_public_access" {
  bucket = google_storage_bucket.image_gallery.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

// Add public access for docs bucket
resource "google_storage_bucket_iam_member" "docs_public_access" {
  bucket = google_storage_bucket.blog_md.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

// Add public access for pdf bucket
resource "google_storage_bucket_iam_member" "pdf_public_access" {
  bucket = google_storage_bucket.pdf_archive.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

output "blog_bucket_name" {
  value = google_storage_bucket.blog_md.name
}

output "image_bucket_name" {
  value = google_storage_bucket.image_gallery.name
}

output "pdf_bucket_name" {
  value = google_storage_bucket.pdf_archive.name
}