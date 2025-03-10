import os
import time
import argparse
import requests
import boto3
from typing import Optional, Dict, Any


class HealthScribe:

    def __init__(self, input_s3_bucket: str, data_access_role_arn: str):
        """
        Initialize the HealthScribe client.
        
        Args:
            s3_bucket: The S3 bucket name where audio files will be stored and results retrieved
            data_access_role_arn: The ARN of the IAM role with necessary permissions
        """
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        self.s3_bucket = input_s3_bucket
        self.data_access_role_arn = data_access_role_arn
        self.healthscribe_session = boto3.session.Session(
                region_name=self.region,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
        )
        self.s3 = self.healthscribe_session.client('s3')
        self.transcribe_medical = self.healthscribe_session.client("transcribe")
    
    def fetch_summary(self, s3_bucket , summary_uri: str) -> str:
        """
        Fetches the summary.json file using a pre-signed URL and formats it into plain text.
        
        Args:
            summary_uri: The URI of the summary file in S3
            
        Returns:
            Formatted summary text
            
        Raises:
            Exception: If there's an error fetching or processing the summary
        """
        try:
            # Extract the S3 object key from the URI
            object_key = summary_uri.split(f"{s3_bucket}/")[-1]
            # Generate a pre-signed URL for temporary access
            pre_signed_url = self._generate_presigned_url(s3_bucket, object_key)
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
    
    def _generate_presigned_url(self,s3_bucket,  object_key: str, expiration: int = 3600) -> str:
        """
        Generate a pre-signed URL for summary.json to allow temporary public access.
        
        Args:
            object_key: The S3 object key
            expiration: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Pre-signed URL
            
        Raises:
            Exception: If URL generation fails
        """
        try:
            print("Generating presigned URL for JSON file")
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': s3_bucket, 'Key': object_key},
                ExpiresIn=expiration
            )
            print(f"Status: Complete")
            return url
        except Exception as e:
            error_msg = f"Error generating pre-signed URL: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)
    
    def start_transcription(self, job_name: str, audio_file_uri: str,output_s3_bucket:str) -> Dict[str, Any]:
        """
        Starts a transcription job for the provided audio file URL.
        
        Args:
            job_name: Unique identifier for the transcription job
            audio_file_uri: URI of the audio file in S3
            
        Returns:
            Transcription job output
            
        Raises:
            Exception: If job start fails
        """
        print(f"Job Name: {job_name}")
        print(f"Audio File URI: {audio_file_uri}")
        
        # Check for existing jobs
        try:
            existing_jobs = self.transcribe_medical.list_medical_scribe_jobs(Status='IN_PROGRESS', MaxResults=5)
            active_jobs = existing_jobs.get('MedicalScribeJobSummaries', [])
            if active_jobs:
                active_job = active_jobs[0]
                return self._poll_transcription_job(active_job['MedicalScribeJobName'])
        except Exception as e:
            raise Exception(f"Error checking active transcription jobs: {e}")

        # Start new job
        try:
            self.transcribe_medical.start_medical_scribe_job(
                MedicalScribeJobName=job_name,
                Media={'MediaFileUri': audio_file_uri},
                OutputBucketName=output_s3_bucket,
                DataAccessRoleArn=self.data_access_role_arn,
                Settings={'ShowSpeakerLabels': True, 'MaxSpeakerLabels': 2}
            )
        except Exception as e:
            raise Exception(f"Error starting transcription job: Please check the job name specified, do not use the same job name. {str(e)}")

        return self._poll_transcription_job(job_name)
    
    def _poll_transcription_job(self, job_name: str) -> Dict[str, Any]:
        """
        Polls the transcription job status until it is completed or failed.
        
        Args:
            job_name: The name of the transcription job to poll
            
        Returns:
            The completed job output
            
        Raises:
            Exception: If job fails or polling encounters an error
        """
        while True:
            try:
                response = self.transcribe_medical.get_medical_scribe_job(MedicalScribeJobName=job_name)
                status = response['MedicalScribeJob']['MedicalScribeJobStatus']
                print(f"Current status: {status}")
                if status == 'COMPLETED':
                    return response['MedicalScribeJob']['MedicalScribeOutput']
                elif status == 'FAILED':
                    raise Exception(f"Job '{job_name}' failed.")
                time.sleep(15)
            except Exception as e:
                raise Exception(f"Error checking job status: {e}")
    
    def process(self, file_path: str, job_name: str, output_s3_bucket: str , s3_key: Optional[str] = None) -> Dict[str, str]:
        """
        Process an audio file through the HealthScribe pipeline.
        
        Args:
            audio_file: Path to the local audio file
            job_name: Unique identifier for the transcription job
            s3_key: Custom S3 key for the audio file (optional)
            
        Returns:
            Dictionary containing summary and status information
            
        Raises:
            Exception: If any step of the process fails
        """
        print("Starting HealthScribe process...")
        
        if s3_key is None:
            base = os.path.basename(file_path)
            s3_key = base
        
        # Upload audio file to S3
        self.s3.upload_file(file_path, self.s3_bucket, s3_key)
        audio_uri = f"https://{self.s3_bucket}.s3.amazonaws.com/{s3_key}"
        
        # Start transcription
        medical_scribe_output = self.start_transcription(job_name, audio_uri,output_s3_bucket)
        
        # Fetch and process summary
        result = {"status": "completed"}
        if "ClinicalDocumentUri" in medical_scribe_output:
            summary_uri = medical_scribe_output['ClinicalDocumentUri']
            transcription_summary = self.fetch_summary(output_s3_bucket , summary_uri)
            result["summary"] = transcription_summary
            print(f"Summary: {transcription_summary}")
        else:
            transcription_summary = medical_scribe_output.get('ClinicalDocumentText', "No summary found.")
            result["summary"] = transcription_summary
            print(f"Summary: {transcription_summary}")
        
        return result