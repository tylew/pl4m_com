# 🚀 Terraform Setup for GCP Infrastructure

This repository contains Terraform configurations to provision the backend infrastructure for a **personal website/blog**. It sets up **Cloud Run, Firestore, Cloud Storage, and IAM roles** on **Google Cloud Platform (GCP)**.

## 📂 Directory Structure

```
terraform/
│── modules/
│   ├── storage/        # Google Cloud Storage (GCS) module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   ├── firestore/      # Firestore Database module
│   │   ├── main.tf
│   │   ├── variables.tf
│   ├── cloud_run/      # Cloud Run module (Flask API)
│   │   ├── main.tf
│   │   ├── variables.tf
│── main.tf             # Root module, defines all Terraform resources
│── providers.tf        # Terraform provider configuration (Google)
│── variables.tf        # Global variables used across modules
│── outputs.tf          # Outputs important values after deployment
│── README.md           # Documentation for Terraform setup
│── .terraform/         # Terraform state and temporary files (auto-generated)
│── terraform.tfstate   # Terraform state file (stored remotely in GCS)
│── terraform.tfstate.backup # Backup of the last known state
```

---

## 🛠 Prerequisites

Ensure you have the following installed:

- **Terraform** (>=1.3.0) → [Install Guide](https://developer.hashicorp.com/terraform/downloads)
- **Google Cloud CLI (`gcloud`)** → [Install Guide](https://cloud.google.com/sdk/docs/install)
- **GCP Project** (`tylers-platform`) with billing enabled

Authenticate with GCP:

```sh
gcloud auth application-default login
gcloud config set project tylers-platform
```

🏗️ Initial Setup & State Storage in GCP

1️⃣ Initialize Terraform

Run the following to initialize Terraform and configure remote state storage:

```sh
terraform init -reconfigure
```

If Terraform state is missing, manually create the GCS backend bucket:

```sh
gcloud storage buckets create tylers-platform-terraform-state --location=us-central1
```

Then reinitialize Terraform:

```sh
terraform init -reconfigure
```

🔄 Managing Terraform State in GCP

Terraform state is stored in a remote GCS bucket (tylers-platform-terraform-state). To interact with the stored state:

Check Current State

```sh
terraform state list
```

View a Specific Resource

```sh
terraform state show <resource-name>
```

Example:

```sh
terraform state show module.storage.google_storage_bucket.blog_md
```

Manually Pull the Latest State from GCS

```sh
terraform refresh
```

Force Recreate a Resource

```sh
terraform taint <resource-name>
terraform apply -auto-approve
```

Manually Remove a Resource from State (But Keep It in GCP)

```sh
terraform state rm <resource-name>
```

Destroy All Resources

```sh
terraform destroy -auto-approve
```

🚀 Deploying Infrastructure to GCP

1️⃣ Enable Required APIs

Terraform cannot provision resources if APIs are disabled. Run:

```sh
terraform apply -target=google_project_service.enabled_services -auto-approve
```

Wait a few minutes for API activation to propagate.

Verify the APIs are enabled:

```sh
gcloud services list --enabled --project=tylers-platform
```

Expected output:

```sh
NAME                              STATE
cloudresourcemanager.googleapis.com  ENABLED
firestore.googleapis.com             ENABLED
iam.googleapis.com                   ENABLED
run.googleapis.com                    ENABLED
storage.googleapis.com                ENABLED
artifactregistry.googleapis.com       ENABLED
```

If APIs are missing, rerun Terraform:

```sh
terraform apply -auto-approve
```

2️⃣ Deploy Full Terraform Configuration

Once APIs are enabled, apply the full Terraform configuration:

```sh
terraform apply -auto-approve
```

After a successful run, check the deployed resources:

```sh
terraform state list
```

3️⃣ Check Terraform Outputs

Run:

```sh
terraform output
```

Expected output:

```sh
cloud_run_url = "https://flask-api-xyz-uc.a.run.app"
blog_bucket_name = "tylers-platform-blog-md"
image_bucket_name = "tylers-platform-images"
```

This provides:
	•	Cloud Run URL → API endpoint
	•	GCS Bucket Names → Where Markdown files & images are stored

📌 Notes & Troubleshooting

1️⃣ Terraform Fails Due to API Errors

If Terraform fails because a service isn’t enabled, run:

```sh
terraform apply -target=google_project_service.enabled_services -auto-approve
```

Then retry:

```sh
terraform apply -auto-approve
```

2️⃣ Cloud Run Service Not Found

If Cloud Run isn’t provisioned, ensure:
	•	All required APIs are enabled (run.googleapis.com).
	•	Terraform has applied successfully. Wait 5 minutes for API changes to propagate.

3️⃣ Terraform State Issues

If Terraform state is missing or corrupted:

Verify the GCS bucket exists:

```sh
gcloud storage ls gs://tylers-platform-terraform-state
```


Reinitialize Terraform:

```sh
terraform init -reconfigure
```


Pull the latest state:

```sh
terraform refresh
```

4️⃣ Destroying All Infrastructure

To completely remove all infrastructure:

```sh
terraform destroy -auto-approve
```