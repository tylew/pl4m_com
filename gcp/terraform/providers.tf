terraform {
  required_version = ">= 1.3.0"

  backend "gcs" {
    bucket = "tylers-platform-terraform-state"
    prefix = "terraform/state"
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}