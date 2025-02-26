output "load_balancer_ip" {
  description = "Load Balancer IP Address"
  value       = module.load_balancer.load_balancer_ip
}

output "dns_configuration" {
  description = "DNS records that need to be configured"
  value       = module.load_balancer.dns_records
}

output "cloud_run_url" {
  description = "Cloud Run URL"
  value       = module.cloud_run.cloud_run_url
}

