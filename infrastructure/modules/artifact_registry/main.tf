resource "google_artifact_registry_repository" "flask_api_repo" {
  project       = var.project_id
  location      = var.region
  repository_id = "flask-api-repo"
  description   = "Repository for Flask API Docker images"
  format        = "DOCKER"
}