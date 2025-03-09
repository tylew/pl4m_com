variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region"
  type        = string
}

variable "storage_class" {
  description = "Storage class for GCS buckets"
  type        = string
}