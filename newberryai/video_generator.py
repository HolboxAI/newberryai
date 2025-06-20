import boto3
import json
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import asyncio
from datetime import datetime
import gradio as gr
import argparse
import sys
from pathlib import Path
import re

# Load environment variables
load_dotenv()

class VideoGenerator:
    """
    A class for generating videos from text using Amazon Bedrock's Nova model.
    This class provides functionality to create, monitor, and retrieve AI-generated videos.
    """
    
    def __init__(self):
        """Initialize the VideoGenerator with AWS clients and configuration."""
        self.bedrock_runtime = boto3.client('bedrock-runtime')
        self.s3_client = boto3.client('s3')
        self.bucket_name = "bedrock-video-generation-us-east-1-7a0z2a"
        self.model_id = "amazon.nova-reel-v1:1"
        
        if not self.bucket_name:
            raise ValueError("S3_BUCKET_NAME environment variable is not set")

    async def check_status(self, invocation_arn: str) -> Dict[str, Any]:
        """
        Check the status of a video generation job.
        
        Args:
            invocation_arn (str): The ARN of the video generation job
            
        Returns:
            Dict[str, Any]: Status information about the job
            
        Raises:
            Exception: If there's an error checking the status
        """
        try:
            response = self.bedrock_runtime.get_async_invoke(
                invocationArn=invocation_arn
            )
            return response
        except Exception as e:
            raise Exception("Failed to check video generation status")

    async def generate(self, text, seed=42, duration_seconds=6, fps=24, dimension="1280x720"):
        """
        Generate a video using Amazon Nova based on the provided text prompt.
        Args:
            text (str): Text prompt for video generation
            seed (int): Seed for video generation
            duration_seconds (int): Duration of the video in seconds
            fps (int): Frames per second
            dimension (str): Video dimensions (width x height)
        Returns:
            dict: Information about the generated video
        """
        try:
            model_input = {
                "taskType": "TEXT_VIDEO",
                "textToVideoParams": {
                    "text": text
                },
                "videoGenerationConfig": {
                    "durationSeconds": duration_seconds,
                    "fps": fps,
                    "dimension": dimension,
                    "seed": seed
                }
            }
            output_config = {
                "s3OutputDataConfig": {
                    "s3Uri": f"s3://{self.bucket_name}"
                }
            }
            response = self.bedrock_runtime.start_async_invoke(
                modelId=self.model_id,
                modelInput=model_input,
                outputDataConfig=output_config
            )
            return {
                "job_id": response["invocationArn"],
                "status": "STARTED",
                "message": "Video generation job started successfully",
                "video_url": None
            }
        except Exception as e:
            raise Exception("Failed to generate video")

    def get_video_url(self, job_id: str) -> str:
        """
        Generate a presigned URL for the generated video.
        
        Args:
            job_id (str): The ID of the video generation job
            
        Returns:
            str: A presigned URL to access the video
            
        Raises:
            Exception: If there's an error generating the URL
        """
        try:
            return self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': f'{job_id}/output.mp4'
                },
                ExpiresIn=3600  # URL expires in 1 hour
            )
        except Exception as e:
            raise Exception("Failed to generate video URL")

    async def wait_for_completion(self, job_id, timeout=300):
        start_time = datetime.now()
        while True:
            if (datetime.now() - start_time).total_seconds() > timeout:
                raise TimeoutError("Video generation timed out")
            status = await self.check_status(job_id)
            if status["status"].lower() == "completed":
                video_url = self.get_video_url(job_id)
                video_url = re.sub(r'/arn%3Aaws%3Abedrock%3Aus-east-1%3A992382417943%3Aasync-invoke([^?]*)(\?.*)?', r'\1', video_url)
                return {
                    "job_id": job_id,
                    "status": "COMPLETED",
                    "message": "Video generation completed successfully",
                    "video_url": video_url
                }
            elif status["status"].lower() == "failed":
                return {
                    "job_id": job_id,
                    "status": "FAILED",
                    "message": f"Video generation failed: {status.get('error', 'Unknown error')}",
                    "video_url": None
                }
            await asyncio.sleep(50)

    def start_gradio(self):
        def generate_video_interface(text, duration, fps, dimension, seed):
            try:
                loop = asyncio.get_event_loop()
                response = loop.run_until_complete(
                    self.generate(text, seed, duration, fps, dimension)
                )
                final_response = loop.run_until_complete(
                    self.wait_for_completion(response["job_id"])
                )
                return final_response["video_url"]
            except Exception as e:
                return f"Error: {str(e)}"

        # Create Gradio interface
        interface = gr.Interface(
            fn=generate_video_interface,
            inputs=[
                gr.Textbox(label="Text Prompt", placeholder="Enter your video description..."),
                gr.Slider(minimum=1, maximum=30, value=6, step=1, label="Duration (seconds)"),
                gr.Slider(minimum=1, maximum=60, value=24, step=1, label="FPS"),
                gr.Dropdown(
                    choices=["1280x720", "1920x1080", "3840x2160"],
                    value="1280x720",
                    label="Video Dimension"
                ),
                gr.Number(value=42, label="Seed", precision=0)
            ],
            outputs=gr.Video(label="Generated Video"),
            title="NewberryAI Video Generator",
            description="Generate videos from text using Amazon Bedrock's Nova model",
            examples=[
                ["A beautiful sunset over the ocean", 6, 24, "1280x720", 42],
                ["A futuristic city with flying cars", 10, 30, "1920x1080", 123],
            ]
        )
        
        return interface.launch(share=True)

    def run_cli(self):
        print("Video Generator AI Assistant initialized")
        print("Type 'exit' or 'quit' to end the conversation.")
        while True:
            text = input("\nEnter your video description: ")
            if text.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            try:
                print("Starting video generation...")
                loop = asyncio.get_event_loop()
                response = loop.run_until_complete(self.generate(text))
                print("Waiting for video generation to complete...")
                final_response = loop.run_until_complete(self.wait_for_completion(response["job_id"]))
                if final_response["status"] == "COMPLETED":
                    print(f"Video generated successfully!")
                    print(f"Video URL: {final_response['video_url']}")
                else:
                    print(f"Video generation failed: {final_response['message']}")
            except Exception as e:
                print(f"Error: {str(e)}")

if __name__ == "__main__":
    VideoGenerator().run_cli()
