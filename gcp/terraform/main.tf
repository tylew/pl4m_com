resource "google_project_service" "enabled_services" {
  for_each = toset([
    "run.googleapis.com",                   # Cloud Run
    "firestore.googleapis.com",             # Firestore
    "storage.googleapis.com",               # Cloud Storage
    "iam.googleapis.com",                   # IAM
    "artifactregistry.googleapis.com",      # Artifact Registry for container storage
    "cloudresourcemanager.googleapis.com",  # Required for IAM and project permissions
    "compute.googleapis.com",                # Required for Load Balancer
    "certificatemanager.googleapis.com"     # Required for Load Balancer
  ])

  project = var.project_id
  service = each.key
  disable_on_destroy = false
}

module "artifact_registry" {
  source     = "./modules/artifact_registry"
  project_id = var.project_id
  region     = var.region
}

module "storage" {
  source        = "./modules/storage"
  project_id    = var.project_id
  region        = var.region
  storage_class = var.storage_class
}

module "firestore" {
  source     = "./modules/firestore"
  project_id = var.project_id
  metadata_collections = var.metadata_collections
}

module "cloud_run" {
  source     = "./modules/cloud_run"
  project_id = var.project_id
  region     = var.region
}

module "load_balancer" {
  source              = "./modules/load_balancer"
  project_id          = var.project_id
  region              = var.region
  images_bucket_name  = "tylers-platform-images"
  docs_bucket_name    = "tylers-platform-blog-md"
  domain              = "pl4m.com"
  api_backend_service = module.cloud_run.api_backend_service
}