resource "google_firestore_database" "default" {
  project     = var.project_id
  name        = "(default)"
  location_id = "nam5"
  type        = "FIRESTORE_NATIVE"
}

# Soft delete with created_at index
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

# Soft delete with updated_at index
resource "google_firestore_index" "soft_delete_updated_at" {
  for_each   = toset(var.metadata_collections)
  project    = var.project_id
  collection = each.value

  fields {
    field_path = "deleted_at"
    order      = "ASCENDING"
  }
  fields {
    field_path = "updated_at"
    order      = "DESCENDING"
  }
  fields {
    field_path = "__name__"
    order      = "ASCENDING"
  }
}

resource "google_firestore_index" "soft_delete_updated_at_nd" {
  for_each   = toset(var.metadata_collections)
  project    = var.project_id
  collection = each.value

  fields {
    field_path = "deleted_at"
    order      = "ASCENDING"
  }
  fields {
    field_path = "updated_at"
    order      = "DESCENDING"
  }
  fields {
    field_path = "__name__"
    order      = "DESCENDING"
  }
}

resource "google_firestore_index" "soft_delete_updated_at_asc" {
  for_each   = toset(var.metadata_collections)
  project    = var.project_id
  collection = each.value

  fields {
    field_path = "deleted_at"
    order      = "ASCENDING"
  }
  fields {
    field_path = "updated_at"
    order      = "ASCENDING"
  }
  fields {
    field_path = "__name__"
    order      = "ASCENDING"
  }
}

# Soft delete with updated_at and created_at index
resource "google_firestore_index" "soft_delete_updated_created_at" {
  for_each   = toset(var.metadata_collections)
  project    = var.project_id
  collection = each.value

  fields {
    field_path = "deleted_at"
    order      = "ASCENDING"
  }
  fields {
    field_path = "updated_at"
    order      = "DESCENDING"
  }
  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }
  fields {
    field_path = "__name__"
    order      = "DESCENDING"
  }
}

# Tags with created_at index
resource "google_firestore_index" "tags_created_at" {
  for_each   = toset(var.metadata_collections)
  project    = var.project_id
  collection = each.value

  fields {
    field_path   = "tags"
    array_config = "CONTAINS"
  }
  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }
}

# Title with created_at index (both orders)
resource "google_firestore_index" "title_created_at" {
  for_each   = toset(var.metadata_collections)
  project    = var.project_id
  collection = each.value

  fields {
    field_path = "title"
    order      = "ASCENDING"
  }
  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }
}

resource "google_firestore_index" "title_created_at_asc" {
  for_each   = toset(var.metadata_collections)
  project    = var.project_id
  collection = each.value

  fields {
    field_path = "title"
    order      = "ASCENDING"
  }
  fields {
    field_path = "created_at"
    order      = "ASCENDING"
  }
}

# Taken_at with created_at index (for images)
resource "google_firestore_index" "taken_at_created_at" {
  for_each   = toset(var.metadata_collections)
  project    = var.project_id
  collection = each.value

  fields {
    field_path = "taken_at"
    order      = "DESCENDING"
  }
  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }
}

# Updated_at with created_at index (both orders)
resource "google_firestore_index" "updated_at_created_at" {
  for_each   = toset(var.metadata_collections)
  project    = var.project_id
  collection = each.value

  fields {
    field_path = "updated_at"
    order      = "DESCENDING"
  }
  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }
}

resource "google_firestore_index" "updated_at_created_at_asc" {
  for_each   = toset(var.metadata_collections)
  project    = var.project_id
  collection = each.value

  fields {
    field_path = "updated_at"
    order      = "DESCENDING"
  }
  fields {
    field_path = "created_at"
    order      = "ASCENDING"
  }
}

# Tags with soft delete, updated_at, and created_at index
resource "google_firestore_index" "tags_soft_delete_updated_created_at" {
  for_each   = toset(var.metadata_collections)
  project    = var.project_id
  collection = each.value

  fields {
    field_path   = "tags"
    array_config = "CONTAINS"
  }
  fields {
    field_path = "deleted_at"
    order      = "ASCENDING"
  }
  fields {
    field_path = "updated_at"
    order      = "DESCENDING"
  }
  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }
  fields {
    field_path = "__name__"
    order      = "DESCENDING"
  }
}

# Tags with soft delete, updated_at, and created_at index (ascending)
resource "google_firestore_index" "tags_soft_delete_updated_created_at_asc" {
  for_each   = toset(var.metadata_collections)
  project    = var.project_id
  collection = each.value

  fields {
    field_path   = "tags"
    array_config = "CONTAINS"
  }
  fields {
    field_path = "deleted_at"
    order      = "ASCENDING"
  }
  fields {
    field_path = "updated_at"
    order      = "ASCENDING"
  }
  fields {
    field_path = "created_at"
    order      = "ASCENDING"
  }
  fields {
    field_path = "__name__"
    order      = "ASCENDING"
  }
}

# Soft delete with created_at index (ascending)
resource "google_firestore_index" "soft_delete_created_at_asc" {
  for_each   = toset(var.metadata_collections)
  project    = var.project_id
  collection = each.value

  fields {
    field_path = "deleted_at"
    order      = "ASCENDING"
  }
  fields {
    field_path = "created_at"
    order      = "ASCENDING"
  }
  fields {
    field_path = "__name__"
    order      = "ASCENDING"
  }
}

# Tags with soft delete and updated_at index (ascending)
resource "google_firestore_index" "tags_soft_delete_updated_at_asc" {
  for_each   = toset(var.metadata_collections)
  project    = var.project_id
  collection = each.value

  fields {
    field_path   = "tags"
    array_config = "CONTAINS"
  }
  fields {
    field_path = "deleted_at"
    order      = "ASCENDING"
  }
  fields {
    field_path = "updated_at"
    order      = "ASCENDING"
  }
  fields {
    field_path = "__name__"
    order      = "ASCENDING"
  }
}