# Audio-Video-Transcriber-Backend

Backend service for transcribing audio and video files. Generates GCS signed URLs for file uploads using service account impersonation.

## Features

- FastAPI application with V4 signed URL generation
- No service account JSON keys required (uses ADC/impersonation)
- Cloud Run ready

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export BUCKET_NAME="your-bucket-name"

# Authenticate using gcloud (with impersonation if needed)
gcloud auth application-default login
# Or with impersonation:
# gcloud auth application-default login --impersonate-service-account=SA_EMAIL

# Run locally
uvicorn main:app --reload --port 8080
```

## Deploy to Cloud Run

```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Deploy
gcloud run deploy gcs-signed-url-service \
  --source . \
  --region us-central1 \
  --set-env-vars BUCKET_NAME=your-bucket-name \
  --allow-unauthenticated
```

## IAM Permissions

The Cloud Run service account needs:
- `roles/storage.objectAdmin` on the bucket (to create signed URLs)
- `roles/iam.serviceAccountTokenCreator` on itself (for signing)

```bash
# Grant permissions (replace with your values)
gcloud storage buckets add-iam-policy-binding gs://YOUR_BUCKET \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"
```

## API Usage

### Generate Upload URL

**POST** `/generate-upload-url`

```json
{
  "file_name": "uploads/my-file.mp4",
  "content_type": "video/mp4"
}
```

**Response:**

```json
{
  "upload_url": "https://storage.googleapis.com/...",
  "file_name": "uploads/my-file.mp4"
}
```

### Upload File Using Signed URL

```bash
curl -X PUT -H "Content-Type: video/mp4" \
  --upload-file my-file.mp4 \
  "SIGNED_URL_HERE"
```

### Health Check

**GET** `/health`

```json
{
  "status": "healthy"
}
