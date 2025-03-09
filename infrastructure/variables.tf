variable "project_id" {
  description = "The GCP project ID"
  type        = string
  default     = "tylers-platform"
}

variable "region" {
  description = "Default region for resources"
  type        = string
  default     = "us-central1"
}

variable "storage_class" {
  description = "Storage class for GCS buckets"
  type        = string
  default     = "STANDARD"
}

variable "metadata_collections" {
  description = "List of Firestore metadatacollections to apply indexes to"
  type        = list(string)
  default     = [
    "tylers-platform-documents", 
    "tylers-platform-images", 
    "tylers-platform-blog", 
    "pl4m-content-library"
  ]
}