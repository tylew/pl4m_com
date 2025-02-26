# 🐍 Flask API Container

This directory contains the Flask API container configuration for the personal website/blog backend. It's designed to run on Google Cloud Run.

## 📂 Directory Structure 

```sh
gcp/containers/flask_api/
├── Dockerfile
├── deploy.sh
├── requirements.txt
├── src/
```

## 🚀 Deployment Options

### Local Development

Run the API locally for development:

```sh
./deploy.sh local
```

This will:
- Build a local Docker image
- Run the container on port 8080
- Mount the code directory for live reloading

### Cloud Run Deployment

Deploy to Google Cloud Run:

```sh
./deploy.sh deploy
```

This will:
1. Authenticate with Google Artifact Registry
2. Build for linux/amd64 platform
3. Push to Artifact Registry
4. Deploy to Cloud Run
5. Output the service URL

## 🔧 Configuration

The container is configured with:
- Python 3.9 slim base image
- Gunicorn WSGI server
- 512Mi memory
- 1 CPU
- Port 8080
- Unbuffered Python output for better logging

## 📝 Environment Variables

- `PORT`: Server port (default: 8080)
- `NAME`: Example variable for hello world (default: "World") 