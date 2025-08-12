from .gpt_agent import GptAgent
import tempfile
import os

# Summarizer Prompt
Sys_Prompt_Summarizer = """You are an AI document summarizer. Your task is to:

1. Read and analyze the provided document content thoroughly
2. Identify the main topic, key arguments, and important findings
3. Extract the most relevant information and data points
4. Provide a comprehensive summary that includes:
   - Main topic and purpose of the document
   - Key findings and conclusions
   - Important data, statistics, or evidence mentioned
   - Any recommendations or future implications
   - Overall significance of the content

Format your response as a clear, well-structured summary that captures the essence of the document. Be thorough but concise, focusing on the most important information that would be valuable to someone who hasn't read the full document."""

# Chat Prompt
Sys_Prompt_Chat = """
You are a highly advanced, friendly, and knowledgeable AI chat assistant.

Instructions:
- Engage in natural, helpful, and polite conversation with the user.
- Answer questions accurately and thoroughly, providing step-by-step explanations when needed.
- If the user asks for advice, recommendations, or opinions, provide well-reasoned and evidence-based responses.
- If the user uploads a file, analyze its content and answer questions about it.
- Always clarify ambiguous questions by asking for more details.
- If you do not know the answer, say so honestly and suggest where the user might find more information.
- Use clear, concise, and professional language.
- Avoid making up facts or providing misleading information.
- If the user requests a summary, analysis, or specific task, follow the instructions precisely.

Output:
- Respond directly to the user's query.
- If the user's request is unclear, ask clarifying questions.
"""

# Image Analysis Prompt
Sys_Prompt_Image = """You are an expert AI image analysis assistant.

Produce a concise, decision‑useful analysis.

Output format (strict):
- Overview: 1 sentence summarizing the image.
- Key elements (max 5 bullets): concrete objects/people/scenes.
- Text (if any): brief transcription or "none".
- Notable insights (max 3 bullets): context, anomalies, or quality notes.
- Answer: if a question was asked, answer in ≤2 sentences.

Rules:
- Keep the entire response within 150–180 words.
- Prefer specificity over verbosity; avoid repetition and generic descriptions.
- Do not speculate beyond what is visibly supported.
"""

# Agent Prompt
Sys_Prompt_Agent = """
You are an advanced AI agent specializing in reasoning, planning, and executing complex tasks.

Instructions:
- Carefully read and understand the user's instruction or question.
- Break down complex tasks into clear, logical steps.
- Provide detailed, step-by-step solutions or action plans.
- If the task involves calculations, show all work and explain your reasoning.
- If the user uploads a file, analyze it and incorporate relevant information into your response.
- If the user's request is ambiguous, ask clarifying questions before proceeding.
- Always check your work for accuracy and completeness.
- Use professional, precise, and neutral language.
- If you cannot complete a task, explain why and suggest alternatives.

Output:
- Provide a clear, actionable response or solution.
- If the task is not possible, explain the limitations.
"""

class FeatureGptSummarizer:
    """
    AI-powered document summarization using GPT-5 (GptAgent).
    """
    def __init__(self):
        self.assistant = GptAgent(system_prompt=Sys_Prompt_Summarizer)

    def start_gradio(self):
        self.assistant.launch_gradio(
            title="GPT-5 Document Summarizer",
            description="Extract and summarize your document with GPT-5",
            input_text_label="Additional instructions (optional)",
            input_files_label="Upload document (required)",
            output_label="Summary"
        )

    def run_cli(self):
        print("GPT-5 Document Summarizer AI Assistant initialized")
        print("Type 'exit' or 'quit' to end the conversation.")
        while True:
            user_input = input("\nEnter your document path: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            print("\nAI Assistant: ", end="")
            response = self.ask(user_input)
            print(response)

    def ask(self, file_path, **kwargs):
        if not isinstance(file_path, str):
            return "Error: Please provide a valid document path."
        
        # Check if file exists
        if not os.path.exists(file_path):
            return f"Error: File not found at {file_path}"
        
        # For summarizer, we want to analyze the document content
        # Pass the file_path to the agent's ask method
        return self.assistant.ask(file_path=file_path, **kwargs)

class FeatureGptChat:
    """
    AI-powered chat assistant using GPT-5 (GptAgent).
    """
    def __init__(self):
        self.assistant = GptAgent(system_prompt=Sys_Prompt_Chat)

    def start_gradio(self):
        import gradio as gr
        def gradio_callback(query):
            try:
                if not query:
                    return "Please enter a message."
                result = self.ask(query)
                return result if result else "No response from model."
            except Exception as e:
                return f"Error: {e}"
        with gr.Blocks(title="GPT-5 Chat Assistant") as iface:
            gr.Markdown("# GPT-5 Chat Assistant")
            text_input = gr.Textbox(label="Your message", lines=3)
            submit_btn = gr.Button("Submit")
            output = gr.Textbox(label="AI's response", lines=10)
            submit_btn.click(fn=gradio_callback, inputs=[text_input], outputs=output)
        iface.launch()

    def run_cli(self):
        print("GPT-5 Chat Assistant initialized")
        print("Type 'exit' or 'quit' to end the conversation.")
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            print("\nAI Assistant: ", end="")
            response = self.ask(user_input)
            print(response)

    def ask(self, question, **kwargs):
        if not isinstance(question, str):
            return "Error: Please provide a valid question."
        return self.assistant.ask(question=question, **kwargs)

class FeatureGptImage:
    """
    AI-powered image analysis using GPT-5 (GptAgent).
    """
    def __init__(self):
        self.assistant = GptAgent(system_prompt=Sys_Prompt_Image)

    def start_gradio(self):
        self.assistant.launch_gradio(
            title="GPT-5 Image Analyzer",
            description="Upload an image and get a detailed analysis with GPT-5.",
            input_text_label="Question about the image (optional)",
            input_files_label="Upload image (required)",
            output_label="Image Analysis"
        )

    def run_cli(self):
        print("GPT-5 Image Analyzer initialized")
        print("Type 'exit' or 'quit' to end the conversation.")
        while True:
            user_input = input("\nEnter image path (or 'exit'): ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            print("\nAI Assistant: ", end="")
            response = self.ask(file_path=user_input)
            print(response)

    def ask(self, file_path, **kwargs):
        if not isinstance(file_path, str):
            return "Error: Please provide a valid image path."
        
        # Check if file exists
        if not os.path.exists(file_path):
            return f"Error: File not found at {file_path}"
        
        # Check if it's a valid image file
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in valid_extensions:
            return f"Error: Unsupported image format. Supported formats: {', '.join(valid_extensions)}"
        
        # For image analysis, we want to analyze the image content
        # Pass the file_path to the agent's ask method
        return self.assistant.ask(file_path=file_path, **kwargs)

class FeatureGptAgent:
    """
    AI-powered agent for reasoning and task execution using GPT-5 (GptAgent).
    """
    def __init__(self):
        self.assistant = GptAgent(system_prompt=Sys_Prompt_Agent)

    def start_gradio(self):
        import gradio as gr

        def gradio_callback(text, file):
            try:
                if not text and file is None:
                    return "Please provide an instruction or upload a file."
                temp_file_path = None
                try:
                    if file:
                        original_name = getattr(file, 'name', 'uploaded_file')
                        ext = os.path.splitext(original_name)[1].lower() or ''
                        supported_extensions = ['.pdf', '.csv', '.jpg', '.jpeg', '.png', '.gif', '.webp', '.txt', '.docx', '.xlsx']
                        if ext not in supported_extensions:
                            return f"Unsupported file type: {ext}. Supported types are: {', '.join(supported_extensions)}"
                        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                            temp_file_path = tmp.name
                            with open(original_name, 'rb') as src, open(temp_file_path, 'wb') as dst:
                                dst.write(src.read())
                        if not os.path.exists(temp_file_path) or os.path.getsize(temp_file_path) == 0:
                            return "Error: File was not written correctly"
                    response = self.ask(question=text, file_path=temp_file_path)
                    return response
                except Exception as e:
                    return f"Error processing file: {str(e)}"
                finally:
                    if temp_file_path and os.path.exists(temp_file_path):
                        try:
                            os.remove(temp_file_path)
                        except Exception as e:
                            print(f"Warning: Could not remove temporary file: {str(e)}")
            except Exception as e:
                return f"Error: {e}"

        with gr.Blocks(title="GPT-5 Agent") as iface:
            gr.Markdown("# GPT-5 Agent")
            with gr.Row():
                text_input = gr.Textbox(label="Your instruction or question", lines=3)
            with gr.Row():
                file_input = gr.File(
                    label="Upload file (optional)",
                    file_types=[".txt", ".pdf", ".docx", ".xlsx", ".png", ".jpg", ".jpeg"]
                )
            with gr.Row():
                submit_btn = gr.Button("Submit")
            with gr.Row():
                output = gr.Textbox(label="Agent's response", lines=10)

            submit_btn.click(fn=gradio_callback, inputs=[text_input, file_input], outputs=output)

        iface.launch()

    def run_cli(self):
        print("GPT-5 Agent initialized")
        print("Type 'exit' or 'quit' to end the conversation.")
        while True:
            user_input = input("\nInstruction or question: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            print("\nAgent: ", end="")
            response = self.ask(user_input)
            print(response)

    def ask(self, question, **kwargs):
        if not isinstance(question, str):
            return "Error: Please provide a valid instruction or question."
        
        # Extract file_path from kwargs if provided
        file_path = kwargs.get('file_path')
        
        # For agent tasks, we can have both question and file_path
        # Pass both to the agent's ask method
        return self.assistant.ask(question=question, file_path=file_path, **kwargs)
