import boto3
import json
import logging
import os
import base64
import uuid
from pathlib import Path
from typing import Optional, Dict, List
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import gradio as gr
import asyncio
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create images directory if it doesn't exist
IMAGES_DIR = Path("generated_images")
IMAGES_DIR.mkdir(exist_ok=True)

class ImageGenerator:
    """
    A class for generating images from text using Amazon Bedrock's Titan Image Generator.
    This class provides functionality to create and save AI-generated images.
    """
    
    def __init__(self):
        """Initialize the ImageGenerator with AWS client and configuration."""
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.model_id = "amazon.titan-image-generator-v2:0"
        self.backend_url = os.getenv("BACKEND_URL", "https://demo.holbox.ai/api/demo_backend_v2")

    class ImageRequest(BaseModel):
        """Pydantic model for image generation request parameters."""
        text: str = Field(..., min_length=1, max_length=512, description="Text prompt for image generation")
        width: int = Field(default=1024, ge=512, le=1024, description="Width of the generated image")
        height: int = Field(default=1024, ge=512, le=1024, description="Height of the generated image")
        number_of_images: int = Field(default=1, ge=1, le=4, description="Number of images to generate")
        cfg_scale: int = Field(default=8, ge=1, le=20, description="CFG scale for image generation")
        seed: Optional[int] = Field(default=42, ge=0, le=2147483646, description="Seed for image generation")
        quality: str = Field(default="standard", description="Quality of the generated image")

    class ImageResponse(BaseModel):
        """Pydantic model for image generation response."""
        message: str
        images: List[str]
        local_path: str
        created_at: datetime = Field(default_factory=datetime.now)

    async def generate(self, request: ImageRequest) -> ImageResponse:
        """
        Generate images using Amazon Titan Image Generator.
        
        Args:
            request (ImageRequest): The image generation request parameters
            
        Returns:
            ImageResponse: Information about the generated images
            
        Raises:
            Exception: If there's an error generating the images
        """
        try:
            # Prepare the request payload
            model_input = {
                "textToImageParams": {
                    "text": request.text
                },
                "taskType": "TEXT_IMAGE",
                "imageGenerationConfig": {
                    "cfgScale": request.cfg_scale,
                    "seed": request.seed,
                    "quality": request.quality,
                    "width": request.width,
                    "height": request.height,
                    "numberOfImages": request.number_of_images,
                }
            }

            logger.info(f"Model input: {json.dumps(model_input, indent=2)}")

            # Generate the image
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(model_input)
            )

            # Parse the response
            response_body = json.loads(response.get('body').read())
            logger.info(f"Model response: {json.dumps(response_body, indent=2)}")

            if 'images' not in response_body:
                raise Exception("No images in response")

            # Process and save images
            image_urls = []
            for image_data in response_body['images']:
                try:
                    # Decode and save the image
                    if isinstance(image_data, str):
                        image_bytes = base64.b64decode(image_data)
                    else:
                        image_bytes = base64.b64decode(image_data.get('data', ''))

                    # Generate unique filename and save
                    filename = f"{uuid.uuid4()}.png"
                    filepath = IMAGES_DIR / filename
                    
                    with open(filepath, "wb") as f:
                        f.write(image_bytes)
                    
                    image_urls.append(f"{self.backend_url}/images/{filename}")
                    logger.info(f"Image saved successfully: {filename}")

                except Exception as e:
                    logger.error(f"Error processing image: {str(e)}")
                    raise Exception("Failed to process generated image")

            return self.ImageResponse(
                message="Images generated successfully",
                images=image_urls,
                local_path=str(IMAGES_DIR)
            )

        except Exception as e:
            logger.error(f"Error in image generation: {str(e)}")
            logger.error(f"Full error details: {str(e.__dict__)}")
            raise Exception("Failed to generate images")

    def start_gradio(self):
        """
        Start a Gradio interface for the image generator.
        This provides a web-based UI for generating images.
        """
        def generate_image_interface(text: str, width: int, height: int, 
                                  number_of_images: int, cfg_scale: int, 
                                  seed: int, quality: str) -> List[str]:
            """Gradio interface function for image generation"""
            try:
                request = self.ImageRequest(
                    text=text,
                    width=width,
                    height=height,
                    number_of_images=number_of_images,
                    cfg_scale=cfg_scale,
                    seed=seed,
                    quality=quality
                )
                
                # Run the async function in the event loop
                loop = asyncio.get_event_loop()
                response = loop.run_until_complete(self.generate(request))
                
                return response.images
            except Exception as e:
                return [f"Error: {str(e)}"]

        # Create Gradio interface
        interface = gr.Interface(
            fn=generate_image_interface,
            inputs=[
                gr.Textbox(label="Text Prompt", placeholder="Enter your image description..."),
                gr.Slider(minimum=512, maximum=1024, value=1024, step=64, label="Width"),
                gr.Slider(minimum=512, maximum=1024, value=1024, step=64, label="Height"),
                gr.Slider(minimum=1, maximum=4, value=1, step=1, label="Number of Images"),
                gr.Slider(minimum=1, maximum=20, value=8, step=1, label="CFG Scale"),
                gr.Number(value=42, label="Seed", precision=0),
                gr.Dropdown(
                    choices=["standard", "premium"],
                    value="standard",
                    label="Quality"
                )
            ],
            outputs=gr.Gallery(label="Generated Images"),
            title="NewberryAI Image Generator",
            description="Generate images from text using Amazon Bedrock's Titan Image Generator",
            examples=[
                ["A beautiful sunset over the ocean", 1024, 1024, 1, 8, 42, "standard"],
                ["A futuristic city with flying cars", 1024, 1024, 2, 10, 123, "premium"],
            ]
        )
        
        return interface.launch(share=True)

    def run_cli(self):
        """
        Run an interactive command-line interface for image generation.
        """
        print("Image Generator AI Assistant initialized")
        print("Type 'exit' or 'quit' to end the conversation.")
        
        while True:
            text = input("\nEnter your image description: ")
            if text.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            try:
                # Create request with default parameters
                request = self.ImageRequest(text=text)
                
                # Generate images
                print("Generating images...")
                loop = asyncio.get_event_loop()
                response = loop.run_until_complete(self.generate(request))
                
                print(f"\nImages generated successfully!")
                print(f"Images saved in: {response.local_path}")
                print("\nImage URLs:")
                for url in response.images:
                    print(url)
                    
            except Exception as e:
                print(f"Error: {str(e)}")

if __name__ == "__main__":
    ImageGenerator.run_cli()
