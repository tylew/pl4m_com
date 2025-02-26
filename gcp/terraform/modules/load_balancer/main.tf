resource "google_compute_global_address" "lb_ip" {
  project = var.project_id
  name    = "lb-ip"
}

resource "google_compute_backend_bucket" "images_backend" {
  name        = "images-backend"
  bucket_name = var.images_bucket_name
  enable_cdn  = true
}

resource "google_compute_backend_bucket" "docs_backend" {
  name        = "docs-backend"
  bucket_name = var.docs_bucket_name
  enable_cdn  = true
}

resource "google_compute_managed_ssl_certificate" "lb_certificate" {
  name = "lb-certificate"

  managed {
    domains = [
      "images.${var.domain}",
      "docs.${var.domain}",
      "api.${var.domain}"
    ]
  }
}

resource "google_compute_url_map" "lb_url_map" {
  name = "lb-url-map"
  default_service = var.api_backend_service

  host_rule {
    hosts        = ["images.${var.domain}"]
    path_matcher = "images-paths"
  }

  path_matcher {
    name            = "images-paths"
    default_service = google_compute_backend_bucket.images_backend.self_link
  }

  host_rule {
    hosts        = ["docs.${var.domain}"]
    path_matcher = "docs-paths"
  }

  path_matcher {
    name            = "docs-paths"
    default_service = google_compute_backend_bucket.docs_backend.self_link
  }

  host_rule {
    hosts        = ["api.${var.domain}"]
    path_matcher = "api-paths"
  }

  path_matcher {
    name            = "api-paths"
    default_service = var.api_backend_service
  }
}

resource "google_compute_target_https_proxy" "lb_https_proxy" {
  name             = "lb-https-proxy"
  url_map          = google_compute_url_map.lb_url_map.id
  ssl_certificates = [google_compute_managed_ssl_certificate.lb_certificate.id]
}

resource "google_compute_global_forwarding_rule" "lb_forwarding_rule" {
  name       = "lb-forwarding-rule"
  target     = google_compute_target_https_proxy.lb_https_proxy.id
  port_range = "443"
  ip_address = google_compute_global_address.lb_ip.address
}

resource "google_compute_url_map" "http_redirect" {
  name = "http-redirect"

  default_url_redirect {
    https_redirect = true
    strip_query    = false
  }
}

resource "google_compute_target_http_proxy" "http_redirect" {
  name    = "http-redirect-proxy"
  url_map = google_compute_url_map.http_redirect.id
}

resource "google_compute_global_forwarding_rule" "http_redirect" {
  name       = "http-redirect-rule"
  target     = google_compute_target_http_proxy.http_redirect.id
  port_range = "80"
  ip_address = google_compute_global_address.lb_ip.address
}