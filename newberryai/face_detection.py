import os
import cv2
import boto3
import tempfile
import shutil
from typing import List, Dict, Optional
from dotenv import load_dotenv
import gradio as gr
from .face_recognigation import FaceRecognition

# Load environment variables
load_dotenv()

class FaceDetection:
    """
    A class for processing video files and detecting faces using AWS Rekognition.
    This class provides functionality to extract frames from videos and detect faces
    using AWS Rekognition service.
    """
    
    def __init__(self):
        """Initialize the FaceDetection with AWS client and configuration."""
        self.rekognition_client = boto3.client("rekognition", region_name="us-east-1")
        self.collection_id = os.getenv("FACE_COLLECTION_ID", "face-db-001")
        # Initialize face recognition for adding faces to collection
        self.face_recognition = FaceRecognition()

    def add_face_to_collection(self, image_path: str, name: str):
        """
        Add a face to the collection using the face recognition module.
        Args:
            image_path (str): Path to the image file
            name (str): Name to associate with the face
        Returns:
            dict: Response from adding face to collection
        """
        return self.face_recognition.add_to_collect(image_path, name)

    def process_video(self, video_path: str, max_frames: int = 20) -> list:
        """
        Process a video file and detect faces in its frames.
        Args:
            video_path (str): Path to the video file
            max_frames (int): Maximum number of frames to process
        Returns:
            List[Dict]: List of detected faces with timestamps and metadata
        """
        print(f"Processing video: {video_path}")
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise Exception("Could not open video file")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        print(f"Total Frames: {total_frames}, FPS: {fps}")

        frame_interval = max(total_frames // max_frames, 1)
        frame_positions = range(0, total_frames, frame_interval)[:max_frames]

        frames_dir = tempfile.mkdtemp()
        detected_faces = []

        try:
            for frame_pos in frame_positions:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                success, frame = cap.read()
                if not success:
                    continue

                timestamp = round(frame_pos / fps, 2)
                print(f"Processing frame at position {frame_pos} ({timestamp}s)")

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                _, img_encoded = cv2.imencode(".jpg", frame_rgb)
                img_bytes = img_encoded.tobytes()

                try:
                    detect_response = self.rekognition_client.detect_faces(
                        Image={"Bytes": img_bytes},
                        Attributes=["DEFAULT"]
                    )

                    if detect_response.get("FaceDetails"):
                        print("Face detected")

                        # Search for matches in the collection
                        search_response = self.rekognition_client.search_faces_by_image(
                            CollectionId=self.collection_id,
                            Image={"Bytes": img_bytes},
                            MaxFaces=1,
                            FaceMatchThreshold=70  # Minimum confidence threshold
                        )

                        if search_response.get("FaceMatches"):
                            matched_face = search_response["FaceMatches"][0]["Face"]
                            external_image_id = matched_face.get("ExternalImageId", "Unknown")
                            confidence = search_response["FaceMatches"][0]["Similarity"]
                            face_id = matched_face.get("FaceId", "Unknown")
                            print(f"Match found: {external_image_id} with confidence {confidence}%")

                            detected_faces.append({
                                "timestamp": timestamp,
                                "external_image_id": external_image_id,
                                "face_id": face_id,
                                "confidence": confidence,
                                "face_details": detect_response["FaceDetails"]
                            })
                        else:
                            print("No match found in collection.")
                            detected_faces.append({
                                "timestamp": timestamp,
                                "face_details": detect_response["FaceDetails"],
                                "external_image_id": None,
                                "face_id": None,
                                "confidence": None
                            })
                    else:
                        print("No face detected.")
                except Exception as e:
                    print(f"Error with frame {frame_pos}: {str(e)}")
        finally:
            cap.release()
            shutil.rmtree(frames_dir)  # Clean up temp directory

        print("Processing complete.")
        return detected_faces

    def start_gradio(self):
        """Launch a web interface for face detection using Gradio."""
        def add_face_interface(image, name):
            """Gradio interface function for adding faces"""
            try:
                # Save the uploaded image temporarily
                temp_path = "temp_face.jpg"
                cv2.imwrite(temp_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
                
                response = self.add_face_to_collection(temp_path, name)
                
                # Clean up temporary file
                os.remove(temp_path)
                
                if response["success"]:
                    return f"Success: Face of {name} added to collection!"
                else:
                    return f"Error: {response['message']}"
            except Exception as e:
                return f"Error: {str(e)}"

        def process_video_interface(video, max_frames):
            # Save the uploaded video to a temp file if it's a numpy array (Gradio 4.x)
            if hasattr(video, 'name'):
                video_path = video.name
            else:
                # fallback for older Gradio versions
                video_path = video
            results = self.process_video(video_path, max_frames)
            
            # Format results for display
            formatted_results = []
            for detection in results:
                result_text = f"Timestamp: {detection['timestamp']}s"
                if detection.get('external_image_id'):
                    result_text += f"\nMatched Face: {detection['external_image_id']}"
                    result_text += f"\nFace ID: {detection['face_id']}"
                    result_text += f"\nConfidence: {detection['confidence']:.2f}%"
                else:
                    result_text += "\nNo match found in collection"
                formatted_results.append(result_text)
            
            return "\n\n".join(formatted_results) if formatted_results else "No faces detected"

        with gr.Blocks(title="Face Detection System", css="""
            .video-preview video {max-width: 400px !important; max-height: 300px !important; border-radius: 10px; box-shadow: 0 2px 8px #0002;}
            .gradio-container {padding: 24px;}
            .gr-box {margin-bottom: 16px;}
            .gr-row {gap: 24px;}
        """) as interface:
            gr.Markdown("# Face Detection System")
            
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
            
            with gr.Tab("Process Video"):
                with gr.Row():
                    with gr.Column():
                        rec_video = gr.Video(label="Upload Video", elem_classes=["video-preview"])
                        max_frames = gr.Slider(minimum=1, maximum=50, value=20, step=1, label="Maximum Frames to Process")
                        rec_button = gr.Button("Process Video")
                        rec_output = gr.Textbox(label="Results", lines=10)
                
                rec_button.click(
                    fn=process_video_interface,
                    inputs=[rec_video, max_frames],
                    outputs=rec_output
                )
        
        return interface.launch(share=True)

    def run_cli(self):
        """Run an interactive command-line interface for face detection."""
        print("Face Detection AI Assistant initialized")
        print("Type 'exit' or 'quit' to end the conversation.")
        print("\nAvailable commands:")
        print("  - add <image_path> <name>: Add a face to the collection")
        print("  - process <video_path> [max_frames]: Process a video for face detection")
        
        while True:
            user_input = input("\nEnter command: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            try:
                parts = user_input.split()
                if len(parts) < 2:
                    print("Invalid command. Please use 'add' or 'process' followed by the file path.")
                    continue
                
                command = parts[0].lower()
                
                if command == "add":
                    if len(parts) < 3:
                        print("Please provide both image path and name for adding a face.")
                        continue
                    image_path = parts[1]
                    name = parts[2]
                    response = self.add_face_to_collection(image_path, name)
                    print(response["message"])
                    if response["success"]:
                        print(f"Face ID: {response['face_id']}")
                
                elif command == "process":
                    video_path = parts[1]
                    max_frames = int(parts[2]) if len(parts) > 2 else 20
                    print("\nProcessing video...")
                    results = self.process_video(video_path, max_frames)
                    
                    print("\nDetection Results:")
                    for detection in results:
                        print(f"\nTimestamp: {detection['timestamp']}s")
                        if detection.get('external_image_id'):
                            print(f"Matched Face: {detection['external_image_id']}")
                            print(f"Face ID: {detection['face_id']}")
                            print(f"Confidence: {detection['confidence']:.2f}%")
                        else:
                            print("No match found in collection")
                
                else:
                    print("Invalid command. Please use 'add' or 'process'.")
                    continue
                
            except Exception as e:
                print(f"Error: {str(e)}")

if __name__ == "__main__":
    face_detection = FaceDetection()
    face_detection.run_cli()
