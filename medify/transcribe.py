import os
import time
import requests
import boto3
from medify.aws_auth import config  # Adjusted to use HealthScribe client
import json

s3 = boto3.client('s3')
transcribe_medical = config()
def fetch_summary(summary_uri,BUCKET_NAME):
    """
    Fetches the summary.json file using a pre-signed URL and formats it into plain text.
    """
    try:
        # Extract the S3 object key from the URI
        object_key = summary_uri.split(f"{BUCKET_NAME}/")[-1]

        # Generate a pre-signed URL for temporary access
        pre_signed_url = generate_presigned_url(BUCKET_NAME, object_key)

        # Fetch the summary.json file from the pre-signed URL
        response = requests.get(pre_signed_url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch summary.json: {response.status_code}, {response.text}")

        summary_json = response.json()

        # Parse the JSON to extract summarized text
        summary_text = ""
        sections = summary_json.get("ClinicalDocumentation", {}).get("Sections", [])
        for section in sections:
            section_name = section.get("SectionName", "Unknown Section")
            summary_text += f"\n{section_name}:\n"
            for summary in section.get("Summary", []):
                summarized_segment = summary.get("SummarizedSegment", "")
                summary_text += f"- {summarized_segment}\n"

        return summary_text.strip()

    except Exception as e:
        raise Exception(f"Error fetching summary: {str(e)}")
    

def generate_presigned_url(bucket_name, object_key, expiration=3600):
    """
    Generate a pre-signed URL for summary.json to allow temporary public access.
    The URL expires in 'expiration' seconds (default: 1 hour).
    """
    s3_client = boto3.client('s3')
    try:
        print("generating presigned url for json file")
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_key},
            ExpiresIn=expiration  # URL expires in 1 hour
        )
        print(f"Status : Complete")
        return url
    except Exception as e:
        print(f"Error generating pre-signed URL: {str(e)}")

        return None
    



def start_transcription(job_name, audio_file_uri,BUCKET_NAME,DATA_ACCESS_ROLE_ARN):
     """Starts a transcription job for the provided audio file URL"""
     print("Job Name : ",job_name)
     print("Audio File URI : ", audio_file_uri)
     try:
          existing_jobs = transcribe_medical.list_medical_scribe_jobs(Status='IN_PROGRESS', MaxResults=5)
          active_jobs = existing_jobs.get('MedicalScribeJobSummaries', [])
          if active_jobs:
               active_job = active_jobs[0]
               return poll_transcription_job(active_job['MedicalScribeJobName'])
     except Exception as e:
          raise Exception(f"Error checking active transcription jobs: {e}")

     try:
          transcribe_medical.start_medical_scribe_job(
               MedicalScribeJobName=job_name,
               Media={'MediaFileUri': audio_file_uri},
               OutputBucketName=BUCKET_NAME,
               DataAccessRoleArn=DATA_ACCESS_ROLE_ARN,
               Settings={'ShowSpeakerLabels': True, 'MaxSpeakerLabels': 2}
          )
     except Exception as e:
          raise Exception(f"Error starting transcription job: Please check the job name specified , do not use the same job name")

     return poll_transcription_job(job_name)


def poll_transcription_job(job_name):
    """Polls the transcription job status until it is completed or failed"""
    while True:
        try:
            response = transcribe_medical.get_medical_scribe_job(MedicalScribeJobName=job_name)
            status = response['MedicalScribeJob']['MedicalScribeJobStatus']
            print(f"Current status: {status}")
            if status == 'COMPLETED':
                return response['MedicalScribeJob']['MedicalScribeOutput']
            elif status == 'FAILED':
                raise Exception(f"Job '{job_name}' failed.")
            time.sleep(15)
        except Exception as e:
            raise Exception(f"Error checking job status: {e}")
        



def healthscribe(audio_file: str, job_name: str,data_access_role_arn : str , s3_bucket: str, s3_key: str = None) -> dict:
    
     if s3_key is None:
          base = os.path.basename(audio_file)
          s3_key = f"{base}"
     
     print("Starting healthscribe process....")
     # Upload audio file to S3
     s3.upload_file(audio_file, s3_bucket, s3_key)
     audio_uri = f"https://{s3_bucket}.s3.amazonaws.com/{s3_key}"
     medical_scribe_output = start_transcription(job_name, audio_uri,s3_bucket,data_access_role_arn)
     if "ClinicalDocumentUri" in medical_scribe_output:
          summary_uri = medical_scribe_output['ClinicalDocumentUri']
          transcription_summary = fetch_summary(summary_uri,s3_bucket)
          print(f"Summary: {transcription_summary}")
     else:
          transcription_summary = medical_scribe_output.get('ClinicalDocumentText', "No summary found.")
          print(f"Summary: {transcription_summary}")
     
    
  
    
