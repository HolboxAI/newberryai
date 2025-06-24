import boto3
import cv2
import os
import gradio as gr
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FaceRecognition:
    """
    A class for face recognition using AWS Rekognition.
    This class provides functionality to add faces to a collection and recognize faces.
    """
    
    def __init__(self):
        self.rekognition_client = boto3.client("rekognition", region_name="us-east-1")
        self.face_collection_id = os.getenv('FACE_COLLECTION_ID', 'face-db-001')
        try:
            self.rekognition_client.create_collection(CollectionId=self.face_collection_id)
        except self.rekognition_client.exceptions.ResourceAlreadyExistsException:
            pass

    def add_to_collect(self, image_path, name):
        """
        Add a face to the AWS Rekognition collection.
        Args:
            image_path (str): Path to the image file
            name (str): Name to associate with the face
        Returns:
            dict: Information about the added face
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Invalid image file or format")
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            _, img_encoded = cv2.imencode('.jpg', image_rgb)
            image_bytes = img_encoded.tobytes()
            response = self.rekognition_client.index_faces(
                CollectionId=self.face_collection_id,
                Image={'Bytes': image_bytes},
                ExternalImageId=name.strip(),
                DetectionAttributes=['ALL']
            )
            if not response['FaceRecords']:
                return {
                    'success': False,
                    'message': 'No face detected in the image',
                    'face_id': None,
                    'name': name
                }
            return {
                'success': True,
                'message': 'Face added successfully',
                'face_id': response['FaceRecords'][0]['Face']['FaceId'],
                'name': name
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error adding face to collection: {str(e)}',
                'face_id': None,
                'name': name
            }

    def recognize_image(self, image_path):
        """
        Recognize a face in the given image by comparing it with faces in the collection.
        Args:
            image_path (str): Path to the image file
        Returns:
            dict: Information about the recognized face
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return {
                    'success': False,
                    'message': 'Invalid image file or format',
                    'name': None,
                    'confidence': None
                }
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            _, img_encoded = cv2.imencode('.jpg', image_rgb)
            image_bytes = img_encoded.tobytes()
            response = self.rekognition_client.search_faces_by_image(
                CollectionId=self.face_collection_id,
                Image={'Bytes': image_bytes},
                MaxFaces=1,
                FaceMatchThreshold=70
            )
            if not response['FaceMatches']:
                return {
                    'success': False,
                    'message': 'No matching face found',
                    'name': None,
                    'confidence': None
                }
            best_match = response['FaceMatches'][0]
            return {
                'success': True,
                'message': 'Face recognized',
                'name': best_match['Face']['ExternalImageId'],
                'confidence': best_match['Similarity']
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error recognizing face: {str(e)}',
                'name': None,
                'confidence': None
            }

    def start_gradio(self):
        """
        Start a Gradio interface for face recognition.
        This provides a web-based UI for adding and recognizing faces.
        """
        def add_face_interface(image, name):
            try:
                temp_path = "temp_face.jpg"
                cv2.imwrite(temp_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
                response = self.add_to_collect(temp_path, name)
                os.remove(temp_path)
                if response['success']:
                    return f"Success: Face of {name} added to collection!"
                else:
                    return f"Error: {response['message']}"
            except Exception as e:
                return f"Error: {str(e)}"

        def recognize_face_interface(image):
            try:
                temp_path = "temp_face.jpg"
                cv2.imwrite(temp_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
                response = self.recognize_image(temp_path)
                os.remove(temp_path)
                if response['success']:
                    return f"Recognized: {response['name']} (Confidence: {response['confidence']:.2f}%)"
                return response['message']
            except Exception as e:
                return f"Error: {str(e)}"

        with gr.Blocks(title="Face Recognition System", css="""
            .image-preview img {max-width: 400px !important; max-height: 300px !important; border-radius: 10px; box-shadow: 0 2px 8px #0002;}
            .gradio-container {padding: 24px;}
            .gr-box {margin-bottom: 16px;}
            .gr-row {gap: 24px;}
        """) as interface:
            gr.Markdown("# Face Recognition System")
            with gr.Tab("Add Face to Collection"):
                with gr.Row():
                    with gr.Column():
                        add_image = gr.Image(label="Upload Face Image", elem_classes=["image-preview"])
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
                        rec_image = gr.Image(label="Upload Face Image", elem_classes=["image-preview"])
                        rec_button = gr.Button("Recognize Face")
                        rec_output = gr.Textbox(label="Result")
                rec_button.click(
                    fn=recognize_face_interface,
                    inputs=[rec_image],
                    outputs=rec_output
                )
        return interface.launch(share=True)

    def run_cli(self):
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
                    response = self.add_to_collect(image_path, name)
                elif command == "recognize":
                    response = self.recognize_image(image_path)
                else:
                    print("Invalid command. Please use 'add' or 'recognize'.")
                    continue
                print(response['message'])
                if response['success']:
                    if response.get('name'):
                        print(f"Name: {response['name']}")
                    if response.get('confidence'):
                        print(f"Confidence: {response['confidence']:.2f}%")
                    if response.get('face_id'):
                        print(f"Face ID: {response['face_id']}")
            except Exception as e:
                print(f"Error: {str(e)}")

if __name__ == "__main__":
    face_recognition = FaceRecognition()
    face_recognition.run_cli()
