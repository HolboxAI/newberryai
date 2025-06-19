import boto3
import json
import os
import base64
import uuid
from pathlib import Path
from typing import Optional, Dict, List
from dotenv import load_dotenv
import gradio as gr
import asyncio
from datetime import datetime

# Load environment variables
load_dotenv()

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

    async def generate(self, text, width=1024, height=1024, number_of_images=1, cfg_scale=8, seed=42, quality="standard"):
        """
        Generate images using Amazon Titan Image Generator.
        Args:
            text (str): Text prompt for image generation
            width (int): Width of the generated image
            height (int): Height of the generated image
            number_of_images (int): Number of images to generate
            cfg_scale (int): CFG scale for image generation
            seed (int): Seed for image generation
            quality (str): Quality of the generated image
        Returns:
            dict: Information about the generated images
        """
        try:
            model_input = {
                "textToImageParams": {
                    "text": text
                },
                "taskType": "TEXT_IMAGE",
                "imageGenerationConfig": {
                    "cfgScale": cfg_scale,
                    "seed": seed,
                    "quality": quality,
                    "width": width,
                    "height": height,
                    "numberOfImages": number_of_images,
                }
            }
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(model_input)
            )
            response_body = json.loads(response.get('body').read())
            if 'images' not in response_body:
                raise Exception("No images in response")
            image_paths = []
            for image_data in response_body['images']:
                try:
                    if isinstance(image_data, str):
                        image_bytes = base64.b64decode(image_data)
                    else:
                        image_bytes = base64.b64decode(image_data.get('data', ''))
                    filename = f"{uuid.uuid4()}.png"
                    filepath = IMAGES_DIR / filename
                    with open(filepath, "wb") as f:
                        f.write(image_bytes)
                    image_paths.append(str(filepath))
                except Exception as e:
                    raise Exception("Failed to process generated image")
            return {
                "message": "Images generated successfully",
                "images": image_paths,
                "local_path": str(IMAGES_DIR)
            }
        except Exception as e:
            raise Exception("Failed to generate images")

    def start_gradio(self):
        """
        Start a Gradio interface for the image generator.
        This provides a web-based UI for generating images.
        """
        def generate_image_interface(text, width, height, number_of_images, cfg_scale, seed, quality):
            try:
                # Call the new generate method with simple arguments
                loop = asyncio.get_event_loop()
                response = loop.run_until_complete(
                    self.generate(text, width, height, number_of_images, cfg_scale, seed, quality)
                )
                return response["images"]
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
                print("Generating images...")
                loop = asyncio.get_event_loop()
                response = loop.run_until_complete(self.generate(text))
                print(f"\nImages generated successfully!")
                print(f"Images saved in: {response['local_path']}")
                print("\nImage Paths:")
                for path in response["images"]:
                    print(path)
                    
            except Exception as e:
                print(f"Error: {str(e)}")

if __name__ == "__main__":
    ImageGenerator().run_cli()
