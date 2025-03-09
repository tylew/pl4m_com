# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Prevent Python from writing pyc files to disc and buffering stdout/stderr
# Ensures that Python output is sent straight to the logs without buffering, 
# which is important for real-time log monitoring and debugging in Cloud Run.
ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
# Copy the pl4m_utils package directory
COPY ../pl4m_utils /app/pl4m_utils
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -e /app/pl4m_utils

# Copy the rest of the application code
COPY . .

# Expose port 8080 for Cloud Run
EXPOSE 8080

# Run the application using Gunicorn
CMD ["gunicorn", "--bind", ":8080", "--workers", "1", "app:app"]