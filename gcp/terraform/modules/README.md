# 🏗️ Terraform Modules

This directory contains modular Terraform configurations for the GCP infrastructure.

## 📂 Modules Overview

### 🗄️ Artifact Registry
- Repository for Docker images
- Configured for the Flask API container
- Location: `artifact_registry/`

### 🏃 Cloud Run
- Manages the Flask API service
- Handles serverless NEG configuration
- Configures IAM permissions
- Location: `cloud_run/`

### 🔥 Firestore
- Sets up the Firestore database
- Configures collection indexes
- Manages metadata collections
- Location: `firestore/`

### ⚖️ Load Balancer
- Global HTTPS load balancer
- SSL certificate management
- Domain routing for subdomains
- CDN configuration
- Location: `load_balancer/`

### 📦 Storage
- GCS bucket configuration
- Public access settings
- CDN integration
- Location: `storage/`

## 📝 Common Variables

All modules accept these base variables:
- `project_id`: GCP Project ID
- `region`: GCP Region

Additional variables are documented in each module's `variables.tf` and `outputs.tf`.
