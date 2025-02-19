import boto3
import os

def config():
    region = os.environ.get("AWS_REGION", "us-east-1")
    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    if aws_access_key_id and aws_secret_access_key:
            client = boto3.client("transcribe", region_name=region, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    else:
        client = boto3.client("transcribe", region_name=region)
    return client
