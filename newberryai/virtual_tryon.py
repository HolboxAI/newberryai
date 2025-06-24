import aiohttp
import uuid
import asyncio
import os
import base64
from pathlib import Path
from typing import Optional, Dict, List
from dotenv import load_dotenv
import gradio as gr
from datetime import datetime
import mimetypes

# Load environment variables
load_dotenv()

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

    def encode_image_with_prefix(self, path):
        with open(path, "rb") as image_file:
            img_data = image_file.read()
            img_ext = path.split('.')[-1].lower()
            # Adding the necessary prefix for base64 encoded images
            return f"data:image/{img_ext};base64," + base64.b64encode(img_data).decode('utf-8')
    
    async def process(self, model_image, garment_image, category="tops"):
        job_id = str(uuid.uuid4())
        self.processing_jobs[job_id] = {"status": "processing", "output": None}
        model_b64 = self.encode_image_with_prefix(model_image)
        garment_b64 = self.encode_image_with_prefix(garment_image)
        payload = {
            "model_image": model_b64,
            "garment_image": garment_b64,
            "category": category,
        }
        try:
            headers = {
                "Authorization": f"Bearer {self.auth_key}",
                "Content-Type": "application/json"
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_url}/run", json=payload, headers=headers) as response:
                    print("POST /run status:", response.status)
                    print("POST /run response:", await response.text())
                    if response.status != 200:
                        error_text = await response.text()
                        self.processing_jobs[job_id]["status"] = "failed"
                        raise Exception(f"API Error: {error_text}")
                    result = await response.json()
                    fashn_id = result.get("id")
                    asyncio.create_task(self._poll_status(job_id, fashn_id))
                    return {"job_id": job_id, "status": "processing"}
        except Exception as error:
            self.processing_jobs[job_id]["status"] = "failed"
            raise Exception(f"Error processing images: {str(error)}")

    async def _poll_status(self, job_id: str, fashn_id: str):
        try:
            headers = {
                "Authorization": f"Bearer {self.auth_key}",
                "Content-Type": "application/json"
            }
            async with aiohttp.ClientSession() as session:
                while True:
                    try:
                        async with session.get(f"{self.api_url}/status/{fashn_id}", headers=headers) as response:
                            print("GET /status status:", response.status)
                            print("GET /status response:", await response.text())
                            if response.status == 200:
                                resp_result = await response.json()
                                if resp_result["status"] == "completed":
                                    self.processing_jobs[job_id]["status"] = "completed"
                                    self.processing_jobs[job_id]["output"] = resp_result["output"]
                                    break
                                elif resp_result["status"] == "failed":
                                    self.processing_jobs[job_id]["status"] = "failed"
                                    break
                        await asyncio.sleep(3)
                    except Exception as e:
                        print("Polling exception:", e)
                        await asyncio.sleep(3)
        except Exception as e:
            print("Outer polling exception:", e)
            self.processing_jobs[job_id]["status"] = "failed"

    async def get_status(self, job_id: str):
        if job_id not in self.processing_jobs:
            raise Exception("Job not found")
        job = self.processing_jobs[job_id]
        return {"job_id": job_id, "status": job["status"], "output": job.get("output")}

    def start_gradio(self):
        """
        Start a Gradio interface for virtual try-on.
        
        This provides a web-based UI for generating virtual try-on images.
        """
        def try_on_interface(model_image: str, garment_image: str, category: str):
            """Gradio interface function for virtual try-on"""
            try:
                # Convert uploaded images to base64
                model_b64 = base64.b64encode(open(model_image, "rb").read()).decode()
                garment_b64 = base64.b64encode(open(garment_image, "rb").read()).decode()
                
                # Run the async function in the event loop
                loop = asyncio.get_event_loop()
                response = loop.run_until_complete(self.process(model_b64, garment_b64, category))
                
                # Wait for completion
                while True:
                    status = loop.run_until_complete(self.get_status(response["job_id"]))
                    if status["status"] in ["completed", "failed"]:
                        break
                    asyncio.sleep(3)
                
                if status["status"] == "completed" and status["output"]:
                    return status["output"]
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
                
                # Process request
                print("Processing virtual try-on...")
                loop = asyncio.get_event_loop()
                response = loop.run_until_complete(self.process(model_b64, garment_b64, category))
                
                # Wait for completion
                while True:
                    status = loop.run_until_complete(self.get_status(response["job_id"]))
                    if status["status"] in ["completed", "failed"]:
                        break
                    asyncio.sleep(3)
                
                if status["status"] == "completed" and status["output"]:
                    print("\nVirtual try-on completed successfully!")
                    print("\nGenerated images:")
                    for url in status["output"]:
                        print(url)
                else:
                    print("\nVirtual try-on failed!")
                    
            except Exception as e:
                print(f"Error: {str(e)}")

if __name__ == "__main__":
    VirtualTryOn().run_cli()
