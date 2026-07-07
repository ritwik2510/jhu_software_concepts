"""boto3 logic"""
from pathlib import Path
import boto3

DEFAULT_BUCKET = "grad-cafe-rps"
DEFAULT_KEY = "applicant_data.json"

def get_s3_client(region_name: str = "us-east-1"):
    """builds boto3 s3 client"""
    session = boto3.session.Session()
    return session.client("s3", region_name=region_name)

def download_applicant_data(
        bucket: str = DEFAULT_BUCKET,
        key: str = DEFAULT_KEY,
        destination: str = "applicant_data_SM.json",
) -> Path:
    """Download the Grad Cafe applicant dataset from S3."""
    s3_client = get_s3_client()
    dest_path = Path(destination)
    s3_client.download_file(bucket, key, str(dest_path))
    return dest_path

def verify_download(path: Path) -> bool:
    """Confirm the downloaded file exists"""
    return path.exists() and path.stat().st_size > 0
