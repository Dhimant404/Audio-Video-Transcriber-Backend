import os
from datetime import timedelta

import google.auth
import google.auth.transport.requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from google.cloud import storage
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="GCS Signed URL Generator")

BUCKET_NAME = os.environ.get("BUCKET_NAME")


class SignedURLRequest(BaseModel):
    file_name: str
    content_type: str


@app.post("/generate-upload-url")
def generate_upload_url(request: SignedURLRequest):
    if not BUCKET_NAME:
        raise HTTPException(status_code=500, detail="BUCKET_NAME environment variable not set")

    try:
        # Get default credentials from the environment
        credentials, project = google.auth.default()

        # Refresh credentials to get the service account email
        auth_request = google.auth.transport.requests.Request()
        credentials.refresh(auth_request)

        # Create storage client
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(request.file_name)

        # Generate V4 signed URL using service account impersonation
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=15),
            method="PUT",
            content_type=request.content_type,
            service_account_email=credentials.service_account_email,
            access_token=credentials.token,
        )

        return {"upload_url": url, "file_name": request.file_name}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    return {"status": "healthy"}
