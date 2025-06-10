import boto3
import json
import logging
import os
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import asyncio
from datetime import datetime
import gradio as gr
import argparse
import sys
from pathlib import Path

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VideoGenerator:
    """
    A class for generating videos from text using Amazon Bedrock's Nova model.
    This class provides functionality to create, monitor, and retrieve AI-generated videos.
    """
    
    def __init__(self):
        """Initialize the VideoGenerator with AWS clients and configuration."""
        self.bedrock_runtime = boto3.client('bedrock-runtime')
        self.s3_client = boto3.client('s3')
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        self.model_id = "amazon.nova-reel-v1:1"
        
        if not self.bucket_name:
            raise ValueError("S3_BUCKET_NAME environment variable is not set")

    class VideoRequest(BaseModel):
        """Pydantic model for video generation request parameters."""
        text: str = Field(..., min_length=1, max_length=512, description="Text prompt for video generation")
        seed: Optional[int] = Field(default=42, ge=0, le=2147483646, description="Seed for video generation")
        duration_seconds: Optional[int] = Field(default=6, ge=1, le=30, description="Duration of the video in seconds")
        fps: Optional[int] = Field(default=24, ge=1, le=60, description="Frames per second")
        dimension: Optional[str] = Field(default="1280x720", description="Video dimensions (width x height)")

    class VideoResponse(BaseModel):
        """Pydantic model for video generation response."""
        job_id: str
        status: str
        message: str
        video_url: Optional[str] = None
        created_at: datetime = Field(default_factory=datetime.now)

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
            logger.error(f"Error checking video generation status: {str(e)}")
            raise Exception("Failed to check video generation status")

    async def generate(self, request: VideoRequest) -> VideoResponse:
        """
        Generate a video using Amazon Nova based on the provided text prompt.
        
        Args:
            request (VideoRequest): The video generation request parameters
            
        Returns:
            VideoResponse: Information about the generated video
            
        Raises:
            Exception: If there's an error generating the video
        """
        try:
            # Prepare the request payload
            model_input = {
                "taskType": "TEXT_VIDEO",
                "textToVideoParams": {
                    "text": request.text
                },
                "videoGenerationConfig": {
                    "durationSeconds": request.duration_seconds,
                    "fps": request.fps,
                    "dimension": request.dimension,
                    "seed": request.seed
                }
            }

            # Configure output location
            output_config = {
                "s3OutputDataConfig": {
                    "s3Uri": f"s3://{self.bucket_name}"
                }
            }

            logger.info(f"Model input: {json.dumps(model_input, indent=2)}")
            logger.info(f"Output config: {json.dumps(output_config, indent=2)}")

            # Start the video generation job
            response = self.bedrock_runtime.start_async_invoke(
                modelId=self.model_id,
                modelInput=model_input,
                outputDataConfig=output_config
            )

            return self.VideoResponse(
                job_id=response["invocationArn"].split("/")[-1],
                status="STARTED",
                message="Video generation job started successfully",
                video_url=None
            )

        except Exception as e:
            logger.error(f"Error in video generation: {str(e)}")
            logger.error(f"Full error details: {str(e.__dict__)}")
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
            logger.error(f"Error generating video URL: {str(e)}")
            raise Exception("Failed to generate video URL")

    async def wait_for_completion(self, job_id: str, timeout: int = 300) -> VideoResponse:
        """
        Wait for the video generation job to complete.
        
        Args:
            job_id (str): The ID of the video generation job
            timeout (int): Maximum time to wait in seconds
            
        Returns:
            VideoResponse: The final status of the video generation
            
        Raises:
            TimeoutError: If the job doesn't complete within the timeout period
        """
        start_time = datetime.now()
        while True:
            if (datetime.now() - start_time).total_seconds() > timeout:
                raise TimeoutError("Video generation timed out")

            status = await self.check_status(job_id)
            if status["status"] == "COMPLETED":
                video_url = self.get_video_url(job_id)
                return self.VideoResponse(
                    job_id=job_id,
                    status="COMPLETED",
                    message="Video generation completed successfully",
                    video_url=video_url
                )
            elif status["status"] == "FAILED":
                return self.VideoResponse(
                    job_id=job_id,
                    status="FAILED",
                    message=f"Video generation failed: {status.get('error', 'Unknown error')}",
                    video_url=None
                )

            await asyncio.sleep(50)  # Wait 50 seconds before checking again

    def start_gradio(self):
        """
        Start a Gradio interface for the video generator.
        This provides a web-based UI for generating videos.
        """
        def generate_video_interface(text: str, duration: int, fps: int, dimension: str, seed: int) -> str:
            """Gradio interface function for video generation"""
            try:
                request = self.VideoRequest(
                    text=text,
                    duration_seconds=duration,
                    fps=fps,
                    dimension=dimension,
                    seed=seed
                )
                
                # Run the async function in the event loop
                loop = asyncio.get_event_loop()
                response = loop.run_until_complete(self.generate(request))
                final_response = loop.run_until_complete(self.wait_for_completion(response.job_id))
                
                return final_response.video_url
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
        """
        Run an interactive command-line interface for video generation.
        """
        print("Video Generator AI Assistant initialized")
        print("Type 'exit' or 'quit' to end the conversation.")
        
        while True:
            text = input("\nEnter your video description: ")
            if text.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            try:
                # Create request with default parameters
                request = self.VideoRequest(text=text)
                
                # Generate video
                print("Starting video generation...")
                loop = asyncio.get_event_loop()
                response = loop.run_until_complete(self.generate(request))
                
                print("Waiting for video generation to complete...")
                final_response = loop.run_until_complete(self.wait_for_completion(response.job_id))
                
                if final_response.status == "COMPLETED":
                    print(f"Video generated successfully!")
                    print(f"Video URL: {final_response.video_url}")
                else:
                    print(f"Video generation failed: {final_response.message}")
                    
            except Exception as e:
                print(f"Error: {str(e)}")

if __name__ == "__main__":
    VideoGenerator.run_cli()
