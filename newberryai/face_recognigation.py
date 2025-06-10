import boto3
import cv2
import os

import gradio as gr
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from fastapi import HTTPException
import numpy as np

# Load environment variables
load_dotenv()

class FaceRequest(BaseModel):
    """Pydantic model for face recognition request parameters."""
    image_path: str = Field(..., description="Path to the image file")
    name: Optional[str] = Field(None, description="Name to associate with the face (for add_to_collect)")

class FaceResponse(BaseModel):
    """Pydantic model for face recognition response."""
    success: bool
    message: str
    name: Optional[str] = None
    confidence: Optional[float] = None
    face_id: Optional[str] = None

class FaceRecognition:
    """
    A class for face recognition using AWS Rekognition.
    This class provides functionality to add faces to a collection and recognize faces.
    """
    
    def __init__(self):
        """Initialize the FaceRecognition with AWS client and configuration."""
        self.rekognition_client = boto3.client("rekognition", region_name="us-east-1")
        self.face_collection_id = os.getenv('FACE_COLLECTION_ID', 'face-db-001')
        
        # Create collection if it doesn't exist
        try:
            self.rekognition_client.create_collection(CollectionId=self.face_collection_id)
            
        except self.rekognition_client.exceptions.ResourceAlreadyExistsException:
            pass

    def add_to_collect(self, request: FaceRequest) -> FaceResponse:
        """
        Add a face to the AWS Rekognition collection.
        
        Args:
            request (FaceRequest): The face addition request parameters
            
        Returns:
            FaceResponse: Information about the added face
            
        Raises:
            HTTPException: If there's an error adding the face
        """
        try:
            # Read and validate image using OpenCV
            image = cv2.imread(request.image_path)
            if image is None:
                raise HTTPException(status_code=400, detail="Invalid image file or format")

            # Convert image to RGB (AWS Rekognition expects RGB)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Convert to JPEG format
            _, img_encoded = cv2.imencode('.jpg', image_rgb)
            image_bytes = img_encoded.tobytes()
            
            # Index the face in the collection
            response = self.rekognition_client.index_faces(
                CollectionId=self.face_collection_id,
                Image={'Bytes': image_bytes},
                ExternalImageId=request.name.strip(),
                DetectionAttributes=['ALL']
            )
            
            if not response['FaceRecords']:
                return FaceResponse(
                    success=False,
                    message="No face detected in the image"
                )
            
            return FaceResponse(
                success=True,
                message="Face added successfully",
                face_id=response['FaceRecords'][0]['Face']['FaceId'],
                name=request.name
            )
        
        except Exception as e:
            return FaceResponse(
                success=False,
                message=f"Error adding face to collection: {str(e)}"
            )

    def recognize_image(self, request: FaceRequest) -> FaceResponse:
        """
        Recognize a face in the given image by comparing it with faces in the collection.
        
        Args:
            request (FaceRequest): The face recognition request parameters
            
        Returns:
            FaceResponse: Information about the recognized face
        """
        try:
            # Read and validate image using OpenCV
            image = cv2.imread(request.image_path)
            if image is None:
                return FaceResponse(
                    success=False,
                    message="Invalid image file or format"
                )

            # Convert image to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Convert to JPEG format
            _, img_encoded = cv2.imencode('.jpg', image_rgb)
            image_bytes = img_encoded.tobytes()
            
            # Search for the face in the collection
            response = self.rekognition_client.search_faces_by_image(
                CollectionId=self.face_collection_id,
                Image={'Bytes': image_bytes},
                MaxFaces=1,
                FaceMatchThreshold=70  # Minimum confidence threshold
            )
            
            if not response['FaceMatches']:
                return FaceResponse(
                    success=False,
                    message="No matching face found"
                )
            
            # Get the best match
            best_match = response['FaceMatches'][0]
            return FaceResponse(
                success=True,
                message="Face recognized",
                name=best_match['Face']['ExternalImageId'],
                confidence=best_match['Similarity']
            )
        
        except Exception as e:
            return FaceResponse(
                success=False,
                message=f"Error recognizing face: {str(e)}"
            )

    def start_gradio(self):
        """
        Start a Gradio interface for face recognition.
        This provides a web-based UI for adding and recognizing faces.
        """
        def add_face_interface(image, name):
            """Gradio interface function for adding faces"""
            try:
                # Save the uploaded image temporarily
                temp_path = "temp_face.jpg"
                cv2.imwrite(temp_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
                
                request = FaceRequest(image_path=temp_path, name=name)
                response = self.add_to_collect(request)
                
                # Clean up temporary file
                os.remove(temp_path)
                
                if response.success:
                    return f"Success: Face of {name} added to collection!"
                else:
                    return f"Error: {response.message}"
            except Exception as e:
                return f"Error: {str(e)}"

        def recognize_face_interface(image):
            """Gradio interface function for recognizing faces"""
            try:
                # Save the uploaded image temporarily
                temp_path = "temp_face.jpg"
                cv2.imwrite(temp_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
                
                request = FaceRequest(image_path=temp_path)
                response = self.recognize_image(request)
                
                # Clean up temporary file
                os.remove(temp_path)
                
                if response.success:
                    return f"Recognized: {response.name} (Confidence: {response.confidence:.2f}%)"
                return response.message
            except Exception as e:
                return f"Error: {str(e)}"

        # Create Gradio interface
        with gr.Blocks(title="Face Recognition System") as interface:
            gr.Markdown("# Face Recognition System")
            
            with gr.Tab("Add Face to Collection"):
                with gr.Row():
                    with gr.Column():
                        add_image = gr.Image(label="Upload Face Image")
                        add_name = gr.Textbox(label="Enter Name")
                        add_button = gr.Button("Add Face")
                        add_output = gr.Textbox(label="Result")
                
                add_button.click(
                    fn=add_face_interface,
                    inputs=[add_image, add_name],
                    outputs=add_output
                )
            
            with gr.Tab("Recognize Face"):
                with gr.Row():
                    with gr.Column():
                        rec_image = gr.Image(label="Upload Face Image")
                        rec_button = gr.Button("Recognize Face")
                        rec_output = gr.Textbox(label="Result")
                
                rec_button.click(
                    fn=recognize_face_interface,
                    inputs=[rec_image],
                    outputs=rec_output
                )
        
        return interface.launch(share=True)

    def run_cli(self):
        """
        Run an interactive command-line interface for face recognition.
        """
        print("Face Recognition System initialized")
        print("Type 'exit' or 'quit' to end the conversation.")
        print("\nAvailable commands:")
        print("  - add <image_path> <name>: Add a face to the collection")
        print("  - recognize <image_path>: Recognize a face in an image")
        
        while True:
            user_input = input("\nEnter command: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            try:
                parts = user_input.split()
                if len(parts) < 2:
                    print("Invalid command. Please use 'add' or 'recognize' followed by the image path.")
                    continue
                
                command = parts[0].lower()
                image_path = parts[1]
                
                if command == "add":
                    if len(parts) < 3:
                        print("Please provide both image path and name for adding a face.")
                        continue
                    name = parts[2]
                    request = FaceRequest(image_path=image_path, name=name)
                    response = self.add_to_collect(request)
                elif command == "recognize":
                    request = FaceRequest(image_path=image_path)
                    response = self.recognize_image(request)
                else:
                    print("Invalid command. Please use 'add' or 'recognize'.")
                    continue
                
                print(response.message)
                if response.success:
                    if response.name:
                        print(f"Name: {response.name}")
                    if response.confidence:
                        print(f"Confidence: {response.confidence:.2f}%")
                    if response.face_id:
                        print(f"Face ID: {response.face_id}")
                
            except Exception as e:
                print(f"Error: {str(e)}")

if __name__ == "__main__":
    face_recognition = FaceRecognition()
    face_recognition.run_cli()
