output "cloud_run_url" {
  value = google_cloud_run_service.flask_api.status[0].url
}

output "api_backend_service" {
  value = google_compute_backend_service.api_backend.self_link
}