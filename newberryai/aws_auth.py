import boto3
import os

def config(service='transcribe'):
    """
    Configures AWS credentials for a specified service.
    service: 'transcribe' or 'bedrock' to configure respective services.
    """
    region = os.environ.get("AWS_REGION", "us-east-1")
    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")

    # Configure client based on service type
    if aws_access_key_id and aws_secret_access_key:
        if service == 'transcribe':
            client = boto3.client(
                "transcribe",
                region_name=region,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )
        elif service == 'bedrock':
            client = boto3.client(
                "bedrock-runtime",
                region_name=region,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )
    else:
        if service == 'transcribe':
            client = boto3.client("transcribe", region_name=region)
        elif service == 'bedrock':
            client = boto3.client("bedrock-runtime", region_name=region)

    return client
