import os
import tempfile
import json
import boto3
import gradio as gr
import base64
from typing import Optional
import pandas as pd
import fitz
from PIL import Image
import numpy as np
from datetime import datetime

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

    def _encode_image(self, file_path: str) -> str:
        """
        Encode an image file to base64.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Base64-encoded image data
        """
        with open(file_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
 
    def _get_media_type(self, file_path: str) -> str:
        """
        Determine the media type based on file extension.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: MIME type of the file
            
        Raises:
            ValueError: If file_path is invalid or extension is not supported
        """
        if not file_path or not isinstance(file_path, str):
            raise ValueError("Invalid file path provided")
        
        extension = os.path.splitext(file_path)[1].lower()
        if not extension:
            raise ValueError("File has no extension")
        
        media_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp"
        }
        return media_types.get(extension, "application/octet-stream")

    def extract(self, doc_path):
        """
        Extract text from a PDF document using PyMuPDF (fitz).
        
        Args:
            doc_path (str): Path to the PDF document
            
        Returns:
            str: Extracted text from the document
            
        Raises:
            FileNotFoundError: If the document doesn't exist
            Exception: For other errors during extraction
        """
        try:
            doc = fitz.open(doc_path)
            text = ""
            for page in doc:
                text += page.get_text()
            
            doc.close()
            
            return text.strip()

        except FileNotFoundError:
            return f"Error: Document not found at path: {doc_path}"
        except Exception as e:
            return f"Error extracting text from document: {str(e)}"

    def _process_csv(self, file_path: str) -> str:
        """
        Process a CSV file and generate comprehensive analysis.
        
        Args:
            file_path (str): Path to the CSV file
            
        Returns:
            str: Analysis of the CSV file including statistics and insights
        """
        try:
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Basic information
            analysis = []
            analysis.append(f"CSV File Analysis:")
            analysis.append(f"Number of rows: {len(df)}")
            analysis.append(f"Number of columns: {len(df.columns)}")
            analysis.append(f"Columns: {', '.join(df.columns)}")
            
            # Data types
            analysis.append("\nData Types:")
            for col, dtype in df.dtypes.items():
                analysis.append(f"{col}: {dtype}")
            
            # Missing values
            missing_values = df.isnull().sum()
            if missing_values.any():
                analysis.append("\nMissing Values:")
                for col, count in missing_values[missing_values > 0].items():
                    analysis.append(f"{col}: {count} missing values")
            
            # Numeric columns analysis
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                analysis.append("\nNumeric Columns Statistics:")
                stats = df[numeric_cols].describe()
                for col in numeric_cols:
                    analysis.append(f"\n{col}:")
                    analysis.append(f"  Mean: {stats[col]['mean']:.2f}")
                    analysis.append(f"  Std: {stats[col]['std']:.2f}")
                    analysis.append(f"  Min: {stats[col]['min']:.2f}")
                    analysis.append(f"  Max: {stats[col]['max']:.2f}")
            
            # Categorical columns analysis
            cat_cols = df.select_dtypes(include=['object']).columns
            if len(cat_cols) > 0:
                analysis.append("\nCategorical Columns Analysis:")
                for col in cat_cols:
                    value_counts = df[col].value_counts()
                    analysis.append(f"\n{col}:")
                    analysis.append(f"  Unique values: {len(value_counts)}")
                    analysis.append(f"  Most common: {value_counts.index[0]} ({value_counts.iloc[0]} occurrences)")
            
            # Correlation analysis for numeric columns
            if len(numeric_cols) > 1:
                corr_matrix = df[numeric_cols].corr()
                analysis.append("\nCorrelation Analysis:")
                for i, col1 in enumerate(numeric_cols):
                    for col2 in numeric_cols[i+1:]:
                        corr = corr_matrix.loc[col1, col2]
                        if abs(corr) > 0.5:  # Only show strong correlations
                            analysis.append(f"  {col1} and {col2}: {corr:.2f}")
            
            return "\n".join(analysis)
            
        except Exception as e:
            return f"Error processing CSV file: {str(e)}"

    def ask(self, question: Optional[str] = None, file_path: Optional[str] = None, return_full_response: bool = False) -> str:
        """
        Send a question or a file (image, PDF, CSV, etc.) or both to Chatbot and get a response.
        At least one of question or file_path must be provided.

        Args:
            question (str, optional): The question to ask Chatbot
            file_path (str, optional): Path to file to include
            return_full_response (bool): If True, return the full response object. Default is False.

        Returns:
            str or dict: Chatbot's response text or full response object
        """
        if question is None and not file_path:
            return "Error: Please provide either a question, a file, or both."

        content = []

        # Add text content if provided
        if question:
            content.append({
                "type": "text",
                "text": question
            })

        # Add content from file if provided
        if file_path:
            ext = os.path.splitext(file_path)[1].lower()
            try:
                if ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
                    # Process image
                    image_data = self._encode_image(file_path)
                    content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": self._get_media_type(file_path),
                            "data": image_data
                        }
                    })
                    if not question:
                        content.insert(0, {
                            "type": "text",
                            "text": "Please analyze this image."
                        })
                elif ext == ".pdf":
                    # Extract text from PDF
                    text = self.extract(file_path)
                    content.append({
                        "type": "text",
                        "text": f"PDF content extracted:\n{text}" 
                    })
                    if not question:
                        content.insert(0, {
                            "type": "text",
                            "text": "Please summarize this PDF document."
                        })
                elif ext == ".csv":
                    # Process CSV file
                    csv_analysis = self._process_csv(file_path)
                    content.append({
                        "type": "text",
                        "text": f"CSV Analysis:\n{csv_analysis}"
                    })
                    if not question:
                        content.insert(0, {
                            "type": "text",
                            "text": "Please analyze this CSV file and provide insights."
                        })
                else:
                    content.append({
                        "type": "text",
                        "text": f"Unsupported file type '{ext}' uploaded."
                    })
            except Exception as e:
                return f"Error processing file '{file_path}': {str(e)}"

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

    def launch_gradio(
        self,
        title: str = "AI Assistant",
        description: str = "Ask a question OR upload a file (PDF, CSV, image, etc.) or both",
        input_text_label: str = "Your question (optional if file is provided)",
        input_files_label: str = "Upload a file (PDF, CSV, image, etc.; optional if question is provided)",
        output_label: str = "AI's response",
        theme: str = "default",
        share: bool = True
    ) -> None:
        """
        Launch a Gradio interface for interacting with Chatbot.
        Allows providing either a question, a single file, or both.

        Args:
            title (str): Title of the Gradio interface
            description (str): Description of the Gradio interface
            input_text_label (str): Label for the input text box
            input_files_label (str): Label for the file upload input
            output_label (str): Label for the output text box
            theme (str): Gradio theme
            share (bool): Whether to create a public link
        """

        def gradio_callback(query: str, file) -> str:
            if not query and not file:
                return "Please provide either a question, a file, or both."
            
            temp_file_path = None
            try:
                if file:
                    # Get the original filename and extension
                    original_name = getattr(file, 'name', 'uploaded_file')
                    ext = os.path.splitext(original_name)[1].lower() or ''
                    
                    # Validate file type
                    supported_extensions = ['.pdf', '.csv', '.jpg', '.jpeg', '.png', '.gif', '.webp']
                    if ext not in supported_extensions:
                        return f"Unsupported file type: {ext}. Supported types are: {', '.join(supported_extensions)}"
                    
                    # For images, convert to JPEG if needed
                    if ext in ['.png', '.gif', '.webp']:
                        try:
                            # Open the image from the file path
                            img = Image.open(original_name)
                            # Convert to RGB if needed (for PNG with transparency)
                            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                                img = img.convert('RGB')
                            # Create temporary file with .jpg extension
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                                temp_file_path = tmp.name
                                img.save(tmp.name, 'JPEG')
                        except Exception as e:
                            return f"Error converting image: {str(e)}"
                    else:
                        # For non-image files, just copy the file
                        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                            temp_file_path = tmp.name
                            with open(original_name, 'rb') as src, open(temp_file_path, 'wb') as dst:
                                dst.write(src.read())
                    
                    # Verify the file was written
                    if not os.path.exists(temp_file_path) or os.path.getsize(temp_file_path) == 0:
                        return "Error: File was not written correctly"
                    
                    response = self.ask(question=query if query else None, file_path=temp_file_path)
                    return response
                    
            except Exception as e:
                return f"Error processing file: {str(e)}"
            finally:
                # Clean up temporary file
                if temp_file_path and os.path.exists(temp_file_path):
                    try:
                        os.remove(temp_file_path)
                    except Exception as e:
                        print(f"Warning: Could not remove temporary file: {str(e)}")


        with gr.Blocks(title=title, theme=theme) as iface:
            gr.Markdown(f"# {title}")
            gr.Markdown(description)

            with gr.Row():
                with gr.Column():
                    text_input = gr.Textbox(label=input_text_label, lines=3)
                    file_input = gr.File(label=input_files_label, file_types=['.pdf', '.csv', '.jpg', '.jpeg', '.png', '.gif', '.webp'])
                    submit_btn = gr.Button("Submit")

                with gr.Column():
                    output = gr.Textbox(label=output_label, lines=10)

            submit_btn.click(
                fn=gradio_callback,
                inputs=[text_input, file_input],
                outputs=output
            )

        iface.launch(share=share)

    def run_cli(self) -> None:
        """
        Run a simple command-line interface with support for either questions or a single file.
        """
        print(f"Multimodal Chatbot Assistant initialized with AI model")
        print("Type 'exit' or 'quit' to end the conversation.")
        print("To ask a question: simply type your question")
        print("To analyze a file: type 'file:' followed by the path to the file")
        print("You can provide both: type 'file:<path> your question'")
        
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            # Check if user wants to include a file
            file_path = None
            query = None
            
            if user_input.startswith("file:"):
                parts = user_input.split(" ", 1)
                file_path = parts[0][5:]  # Remove 'file:' prefix
                
                # Check if there's additional text for a question
                if len(parts) > 1:
                    query = parts[1]
            else:
                # Just a text question
                query = user_input
            
            print("\nChatbot: ", end="")
            answer = self.ask(question=query, file_path=file_path)
            print(answer)
