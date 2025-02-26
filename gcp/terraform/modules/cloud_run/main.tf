# Fetch the default Google Cloud Run service account
data "google_project" "project" {}

# Fetch the default Compute Engine service account (which Cloud Run often uses)
data "google_service_account" "cloud_run_sa" {
  account_id = "${data.google_project.project.number}-compute@developer.gserviceaccount.com"
  project    = var.project_id
}

# Grant Artifact Registry read access to Cloud Run's service account
resource "google_project_iam_binding" "cloud_run_pull_permission" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"

  members = [
    "serviceAccount:${data.google_service_account.cloud_run_sa.email}"
  ]
}

resource "google_cloud_run_service" "flask_api" {
  name     = "flask-api"
  location = var.region

  template {
    spec {
      containers {
        image = "us-central1-docker.pkg.dev/${var.project_id}/flask-api-repo/flask-api:latest"
        ports {
          container_port = 8080
        }
      }
    }
  }
}

resource "google_compute_region_network_endpoint_group" "cloudrun_neg" {
  name                  = "cloudrun-neg"
  network_endpoint_type = "SERVERLESS"
  region               = var.region
  
  cloud_run {
    service = google_cloud_run_service.flask_api.name
  }
}

resource "google_compute_backend_service" "api_backend" {
  name = "api-backend"

  backend {
    group = google_compute_region_network_endpoint_group.cloudrun_neg.id
  }
}

# Allow unauthenticated access to flask_api service
resource "google_cloud_run_service_iam_member" "public_access" {
  location = google_cloud_run_service.flask_api.location
  service  = google_cloud_run_service.flask_api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}