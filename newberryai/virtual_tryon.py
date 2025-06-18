import aiohttp
import uuid
import asyncio
import os
import base64
from pathlib import Path
from typing import Optional, Dict, List
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import gradio as gr
from datetime import datetime
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create output directory if it doesn't exist
OUTPUT_DIR = Path("virtual_tryon_output")
OUTPUT_DIR.mkdir(exist_ok=True)

class VirtualTryOn:
    """
    A class for virtual try-on using the Fashn API.
    This class provides functionality to generate virtual try-on images.
    """
    
    def __init__(self):
        """Initialize the VirtualTryOn with API configuration."""
        self.api_url = os.getenv("FASHN_API_URL")
        self.auth_key = os.getenv("FASHN_AUTH_KEY")
        
        if not self.api_url or not self.auth_key:
            raise ValueError("Missing FASHN_API_URL or FASHN_AUTH_KEY in environment")
        
        # Global storage for processing jobs
        self.processing_jobs = {}

    class TryOnRequest(BaseModel):
        """Pydantic model for virtual try-on request parameters."""
        model_image: str = Field(..., description="Base64 encoded model image")
        garment_image: str = Field(..., description="Base64 encoded garment image")
        category: str = Field(default="tops", description="Category of the garment")

    class TryOnResponse(BaseModel):
        """Pydantic model for virtual try-on response."""
        job_id: str
        status: str
        output: Optional[List[str]] = None
        created_at: datetime = Field(default_factory=datetime.now)

    async def process(self, request: TryOnRequest) -> TryOnResponse:
        """
        Process a virtual try-on request.
        
        Args:
            request (TryOnRequest): The virtual try-on request parameters
            
        Returns:
            TryOnResponse: Information about the processing job
            
        Raises:
            Exception: If there's an error processing the request
        """
        job_id = str(uuid.uuid4())
        
        # Initialize job status
        self.processing_jobs[job_id] = {
            "status": "processing",
            "output": None
        }
        
        payload = {
            "model_image": request.model_image,
            "garment_image": request.garment_image,
            "category": request.category,
        }

        try:
            headers = {
                "Authorization": f"Bearer {self.auth_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_url}/run", json=payload, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        self.processing_jobs[job_id]["status"] = "failed"
                        raise Exception(f"API Error: {error_text}")
                    
                    result = await response.json()
                    fashn_id = result.get("id")
                    
                    # Start background polling
                    asyncio.create_task(self._poll_status(job_id, fashn_id))
                    
                    return self.TryOnResponse(
                        job_id=job_id,
                        status="processing"
                    )

        except Exception as error:
            self.processing_jobs[job_id]["status"] = "failed"
            raise Exception(f"Error processing images: {str(error)}")

    async def _poll_status(self, job_id: str, fashn_id: str):
        """Poll the status of a processing job."""
        try:
            headers = {
                "Authorization": f"Bearer {self.auth_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                while True:
                    try:
                        async with session.get(f"{self.api_url}/status/{fashn_id}", headers=headers) as response:
                            if response.status == 200:
                                resp_result = await response.json()
                                
                                if resp_result["status"] == "completed":
                                    self.processing_jobs[job_id]["status"] = "completed"
                                    self.processing_jobs[job_id]["output"] = resp_result["output"]
                                    break
                                    
                                elif resp_result["status"] == "failed":
                                    self.processing_jobs[job_id]["status"] = "failed"
                                    logger.error("Image processing failed...")
                                    break
                        
                        await asyncio.sleep(3)
                        
                    except Exception as e:
                        logger.error(f"Polling error: {e}")
                        await asyncio.sleep(3)
                        
        except Exception as e:
            self.processing_jobs[job_id]["status"] = "failed"
            logger.error(f"Polling exception: {e}")

    async def get_status(self, job_id: str) -> TryOnResponse:
        """Get the status of a processing job."""
        if job_id not in self.processing_jobs:
            raise Exception("Job not found")
        
        job = self.processing_jobs[job_id]
        return self.TryOnResponse(
            job_id=job_id,
            status=job["status"],
            output=job.get("output")
        )

    def start_gradio(self):
        """
        Start a Gradio interface for virtual try-on.
        
        This provides a web-based UI for generating virtual try-on images.
        """
        def try_on_interface(model_image: str, garment_image: str, category: str) -> List[str]:
            """Gradio interface function for virtual try-on"""
            try:
                # Convert uploaded images to base64
                model_b64 = base64.b64encode(open(model_image, "rb").read()).decode()
                garment_b64 = base64.b64encode(open(garment_image, "rb").read()).decode()
                
                request = self.TryOnRequest(
                    model_image=model_b64,
                    garment_image=garment_b64,
                    category=category
                )
                
                # Run the async function in the event loop
                loop = asyncio.get_event_loop()
                response = loop.run_until_complete(self.process(request))
                
                # Wait for completion
                while True:
                    status = loop.run_until_complete(self.get_status(response.job_id))
                    if status.status in ["completed", "failed"]:
                        break
                    asyncio.sleep(3)
                
                if status.status == "completed" and status.output:
                    return status.output
                else:
                    return ["Error: Processing failed"]
                    
            except Exception as e:
                return [f"Error: {str(e)}"]

        # Create Gradio interface
        interface = gr.Interface(
            fn=try_on_interface,
            inputs=[
                gr.Image(label="Model Image", type="filepath"),
                gr.Image(label="Garment Image", type="filepath"),
                gr.Dropdown(
                    choices=["tops", "bottoms", "dresses", "outerwear"],
                    value="tops",
                    label="Garment Category"
                )
            ],
            outputs=gr.Gallery(label="Generated Images"),
            title="NewberryAI Virtual Try-On",
            description="Generate virtual try-on images using AI",
            examples=[
                ["path/to/model.jpg", "path/to/garment.jpg", "tops"],
                ["path/to/model.jpg", "path/to/dress.jpg", "dresses"],
            ]
        )
        
        return interface.launch(share=True)

    def run_cli(self):
        """
        Run an interactive command-line interface for virtual try-on.
        """
        print("Virtual Try-On AI Assistant initialized")
        print("Type 'exit' or 'quit' to end the conversation.")
        
        while True:
            model_path = input("\nEnter path to model image: ")
            if model_path.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
                
            garment_path = input("Enter path to garment image: ")
            category = input("Enter garment category (tops/bottoms/dresses/outerwear) [default: tops]: ") or "tops"
            
            try:
                # Convert images to base64
                model_b64 = base64.b64encode(open(model_path, "rb").read()).decode()
                garment_b64 = base64.b64encode(open(garment_path, "rb").read()).decode()
                
                # Create request
                request = self.TryOnRequest(
                    model_image=model_b64,
                    garment_image=garment_b64,
                    category=category
                )
                
                # Process request
                print("Processing virtual try-on...")
                loop = asyncio.get_event_loop()
                response = loop.run_until_complete(self.process(request))
                
                # Wait for completion
                while True:
                    status = loop.run_until_complete(self.get_status(response.job_id))
                    if status.status in ["completed", "failed"]:
                        break
                    asyncio.sleep(3)
                
                if status.status == "completed" and status.output:
                    print("\nVirtual try-on completed successfully!")
                    print("\nGenerated images:")
                    for url in status.output:
                        print(url)
                else:
                    print("\nVirtual try-on failed!")
                    
            except Exception as e:
                print(f"Error: {str(e)}")

if __name__ == "__main__":
    VirtualTryOn.run_cli()
