resource "google_firestore_database" "default" {
  project     = var.project_id
  name        = "(default)"
  location_id = "nam5"
  type        = "FIRESTORE_NATIVE"
}

# Loop through collections to create indexes dynamically
resource "google_firestore_index" "soft_delete_created_at" {
  for_each   = toset(var.metadata_collections)
  project    = var.project_id
  collection = each.value

  fields {
    field_path = "deleted_at"
    order      = "ASCENDING"
  }
  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }
}

resource "google_firestore_index" "soft_delete_modified_at" {
  for_each   = toset(var.metadata_collections)
  project    = var.project_id
  collection = each.value

  fields {
    field_path = "deleted_at"
    order      = "ASCENDING"
  }
  fields {
    field_path = "modified_at"
    order      = "DESCENDING"
  }
}