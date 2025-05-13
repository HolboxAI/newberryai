import os
import json
import boto3
import gradio as gr
import base64
from typing import Optional


class HealthChat:

    def __init__(
        self,
        system_prompt: str = "",
        max_tokens: int = 1000

    ):
        session = boto3.Session()
        credentials = session.get_credentials()
        if credentials is None:
            raise ValueError("No AWS credentials found. Please configure AWS credentials.")
        frozen_credentials = credentials.get_frozen_credentials()

        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.aws_access_key_id = frozen_credentials.access_key
        self.aws_secret_access_key = frozen_credentials.secret_key
        self.health_chat_session = boto3.session.Session(
                region_name=self.region,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
        )
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt
        
        if not self.aws_access_key_id or not self.aws_secret_access_key:
            raise ValueError("AWS credentials not found. Please provide them or set environment variables.")
        
        self.runtime = self.health_chat_session.client("bedrock-runtime")
        

    def _encode_image(self, image_path: str) -> str:
        """
        Encode an image file to base64.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Base64-encoded image data
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")


    def ask(self, question: Optional[str] = None, image_path: Optional[str] = None, return_full_response: bool = False) -> str:
        """
        Send a question or an image (or both) to Chatbot and get a response.
        At least one of question or image_path must be provided.

        Args:
            question (str, optional): The question to ask Chatbot
            image_path (str, optional): Path to an image file to include
            return_full_response (bool): If True, return the full response object. Default is False.

        Returns:
            str or dict: Chatbot's response text or full response object
        """
        if question is None and image_path is None:
            return "Error: Please provide either a question, an image, or both."

        content = []

        # Add text content if provided
        if question:
            content.append({
                "type": "text",
                "text": question
            })

        # Add image content if provided
        if image_path:
            try:
                image_data = self._encode_image(image_path)
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": self._get_media_type(image_path),
                        "data": image_data
                    }
                })

                # If no question is provided, add a default prompt for image analysis
                if not question:
                    content.insert(0, {
                        "type": "text",
                        "text": "Please analyze this image."
                    })
            except Exception as e:
                return f"Error processing image: {str(e)}"

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": self.max_tokens,
            "system": self.system_prompt,
            "temperature": 0.0,
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ]
        })

        try:
            response = self.runtime.invoke_model(
                modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
                contentType='application/json',
                body=body,
            )
            
            if return_full_response:
                return response

            response_body = json.loads(response['body'].read())
            return response_body['content'][0]["text"]

        except Exception as e:
            return f"Error: {str(e)}"

    
    def _get_media_type(self, file_path: str) -> str:
        """
        Determine the media type based on file extension.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: MIME type of the file
        """
        extension = os.path.splitext(file_path)[1].lower()
        media_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp"
        }
        
        return media_types.get(extension, "application/octet-stream")

    def launch_gradio(
        self,
        title: str = "AI Assistant",
        description: str = "Ask a question OR upload an image (or both)",
        input_text_label: str = "Your question (optional if image is provided)",
        input_image_label: str = "Upload image (optional if question is provided)",
        output_label: str = "AI's response",
        theme: str = "default",
        share: bool = True
    ) -> None:
        """
        Launch a Gradio interface for interacting with Chatbot.
        Allows providing either a question, an image, or both.
        
        Args:
            title (str): Title of the Gradio interface
            description (str): Description of the Gradio interface
            input_text_label (str): Label for the input text box
            input_image_label (str): Label for the image input
            output_label (str): Label for the output text box
            theme (str): Gradio theme
            share (bool): Whether to create a public link
        """
        def gradio_callback(query: str, image) -> str:
            # Check if at least one input is provided
            if not query and image is None:
                return "Please provide either a question, an image, or both."
            
            # Process image if provided
            temp_image_path = None
            if image is not None:
                temp_image_path = "temp_uploaded_image.jpg"
                image.save(temp_image_path)
            
            # Get response
            response = self.ask(question=query if query else None, 
                               image_path=temp_image_path)
            
            # Clean up
            if temp_image_path and os.path.exists(temp_image_path):
                os.remove(temp_image_path)
                
            return response
        
        with gr.Blocks(title=title, theme=theme) as iface:
            gr.Markdown(f"# {title}")
            gr.Markdown(description)
            
            with gr.Row():
                with gr.Column():
                    text_input = gr.Textbox(label=input_text_label, lines=3)
                    image_input = gr.Image(label=input_image_label, type="pil")
                    submit_btn = gr.Button("Submit")
                
                with gr.Column():
                    output = gr.Textbox(label=output_label, lines=10)
            
            submit_btn.click(
                fn=gradio_callback,
                inputs=[text_input, image_input],
                outputs=output
            )
        
        iface.launch(share=share)
    
    def run_cli(self) -> None:
        """
        Run a simple command-line interface with support for either questions or images.
        """
        print(f"Multimodal Chatbot Assistant initialized with AI model")
        print("Type 'exit' or 'quit' to end the conversation.")
        print("To ask a question: simply type your question")
        print("To analyze an image: type 'image:' followed by the path to the image file")
        print("You can provide both: type 'image:<path> your question'")
        
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            # Check if user wants to include an image
            image_path = None
            query = None
            
            if user_input.startswith("image:"):
                parts = user_input.split(" ", 1)
                image_path = parts[0][6:]  # Remove 'image:' prefix
                
                # Check if there's additional text for a question
                if len(parts) > 1:
                    query = parts[1]
            else:
                # Just a text question
                query = user_input
            
            print("\nChatbot: ", end="")
            answer = self.ask(question=query, image_path=image_path)
            print(answer)