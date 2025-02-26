output "load_balancer_ip" {
  description = "The IP address of the load balancer"
  value       = google_compute_global_address.lb_ip.address
}

output "dns_records" {
  description = "DNS records to configure"
  value = {
    images = "images.${var.domain} -> ${google_compute_global_address.lb_ip.address} (A record)"
    docs   = "docs.${var.domain} -> ${google_compute_global_address.lb_ip.address} (A record)"
    api    = "api.${var.domain} -> ${google_compute_global_address.lb_ip.address} (A record)"
  }
} 