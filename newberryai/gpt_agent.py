import os
import openai
import gradio as gr
import pandas as pd
import fitz
from PIL import Image
import numpy as np
import base64
import tempfile
from typing import Optional
import json

class GptAgent:
    def __init__(self, system_prompt: str = "", max_tokens: int = 1000, model: str = "gpt-5"):
        """
        Initialize GptAgent for GPT-5.
        Args:
            system_prompt (str): System prompt for the LLM.
            max_tokens (int): Max tokens for the LLM response.
            model (str): OpenAI model name (default: gpt-5).
        """
        self.system_prompt = system_prompt
        self.max_tokens = max_tokens
        self.model = model
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        openai.api_key = self.api_key

    def _encode_image(self, file_path: str) -> str:
        with open(file_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def _get_media_type(self, file_path: str) -> str:
        extension = os.path.splitext(file_path)[1].lower()
        media_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp"
        }
        return media_types.get(extension, "application/octet-stream")

    def extract_pdf(self, doc_path):
        try:
            doc = fitz.open(doc_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text.strip()
        except Exception as e:
            return f"Error extracting text from document: {str(e)}"

    def process_csv(self, file_path: str) -> str:
        try:
            df = pd.read_csv(file_path)
            analysis = []
            analysis.append(f"CSV File Analysis:")
            analysis.append(f"Number of rows: {len(df)}")
            analysis.append(f"Number of columns: {len(df.columns)}")
            analysis.append(f"Columns: {', '.join(df.columns)}")
            analysis.append("\nData Types:")
            for col, dtype in df.dtypes.items():
                analysis.append(f"{col}: {dtype}")
            missing_values = df.isnull().sum()
            if missing_values.any():
                analysis.append("\nMissing Values:")
                for col, count in missing_values[missing_values > 0].items():
                    analysis.append(f"{col}: {count} missing values")
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
            cat_cols = df.select_dtypes(include=['object']).columns
            if len(cat_cols) > 0:
                analysis.append("\nCategorical Columns Analysis:")
                for col in cat_cols:
                    value_counts = df[col].value_counts()
                    analysis.append(f"\n{col}:")
                    analysis.append(f"  Unique values: {len(value_counts)}")
                    analysis.append(f"  Most common: {value_counts.index[0]} ({value_counts.iloc[0]} occurrences)")
            if len(numeric_cols) > 1:
                corr_matrix = df[numeric_cols].corr()
                analysis.append("\nCorrelation Analysis:")
                for i, col1 in enumerate(numeric_cols):
                    for col2 in numeric_cols[i+1:]:
                        corr = corr_matrix.loc[col1, col2]
                        if abs(corr) > 0.5:
                            analysis.append(f"  {col1} and {col2}: {corr:.2f}")
            return "\n".join(analysis)
        except Exception as e:
            return f"Error processing CSV file: {str(e)}"

    def ask(self, question: Optional[str] = None, file_path: Optional[str] = None, return_full_response: bool = False) -> str:
        if question is None and not file_path:
            return "Error: Please provide either a question, a file, or both."
        
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        
        if question:
            messages.append({"role": "user", "content": question})
        
        if file_path:
            ext = os.path.splitext(file_path)[1].lower()
            try:
                if ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
                    with open(file_path, "rb") as img_file:
                        image_bytes = img_file.read()
                    messages.append({
                        "role": "user",
                        "content": [
                            {"type": "text", "text": question or "Please analyze this image."},
                            {"type": "image_url", "image_url": {"url": f"data:{self._get_media_type(file_path)};base64,{base64.b64encode(image_bytes).decode()}"}}
                        ]
                    })
                elif ext == ".pdf":
                    text = self.extract_pdf(file_path)
                    messages.append({"role": "user", "content": f"PDF content extracted:\n{text}"})
                elif ext == ".csv":
                    csv_analysis = self.process_csv(file_path)
                    messages.append({"role": "user", "content": f"CSV Analysis:\n{csv_analysis}"})
                else:
                    messages.append({"role": "user", "content": f"Unsupported file type '{ext}' uploaded."})
            except Exception as e:
                return f"Error processing file '{file_path}': {str(e)}"
        
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages
            )
            
            if return_full_response:
                return response
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

    def launch_gradio(self,
        title: str = "GPT-5 Assistant",
        description: str = "Ask a question OR upload a file (PDF, CSV, image, etc.) or both",
        input_text_label: str = "Your question (optional if file is provided)",
        input_files_label: str = "Upload a file (PDF, CSV, image, etc.; optional if question is provided)",
        output_label: str = "AI's response",
        theme: str = "default",
        share: bool = True
    ) -> None:
        def gradio_callback(query: str, file) -> str:
            if not query and not file:
                return "Please provide either a question, a file, or both."
            temp_file_path = None
            try:
                if file:
                    original_name = getattr(file, 'name', 'uploaded_file')
                    ext = os.path.splitext(original_name)[1].lower() or ''
                    supported_extensions = ['.pdf', '.csv', '.jpg', '.jpeg', '.png', '.gif', '.webp']
                    if ext not in supported_extensions:
                        return f"Unsupported file type: {ext}. Supported types are: {', '.join(supported_extensions)}"
                    if ext in ['.png', '.gif', '.webp']:
                        try:
                            img = Image.open(original_name)
                            if img.mode in ('RGBA', 'LA') or (img.mode == 'P'):
                                img = img.convert('RGB')
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                                temp_file_path = tmp.name
                                img.save(tmp.name, 'JPEG')
                        except Exception as e:
                            return f"Error converting image: {str(e)}"
                    else:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                            temp_file_path = tmp.name
                            with open(original_name, 'rb') as src, open(temp_file_path, 'wb') as tmp:
                                tmp.write(src.read())
                    if not os.path.exists(temp_file_path) or os.path.getsize(temp_file_path) == 0:
                        return "Error: File was not written correctly"
                    response = self.ask(question=query if query else None, file_path=temp_file_path)
                    return response
            except Exception as e:
                return f"Error processing file: {str(e)}"
            finally:
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
        print(f"GPT-5 Agent initialized.")
        print("Type 'exit' or 'quit' to end the conversation.")
        print("To ask a question: simply type your question")
        print("To analyze a file: type 'file:' followed by the path to the file")
        print("You can provide both: type 'file:<path> your question'")
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            file_path = None
            query = None
            if user_input.startswith("file:"):
                parts = user_input.split(" ", 1)
                file_path = parts[0][5:]
                if len(parts) > 1:
                    query = parts[1]
            else:
                query = user_input
            print("\nGPT-5: ", end="")
            answer = self.ask(question=query, file_path=file_path)
            print(answer)