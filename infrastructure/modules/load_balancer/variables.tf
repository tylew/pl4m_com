variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
}

variable "images_bucket_name" {
  description = "Bucket name for images"
  type        = string
}

variable "docs_bucket_name" {
  description = "Bucket name for docs"
  type        = string
}

variable "pdf_bucket_name" {
  description = "Bucket name for pdfs"
  type        = string
}

variable "domain" {
  description = "Base domain for services"
  type        = string
}

variable "api_backend_service" {
  description = "The backend service for the API"
  type        = string
}