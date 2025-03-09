variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "metadata_collections" {
  description = "List of Firestore metadatacollections to apply indexes to"
  type        = list(string)
}