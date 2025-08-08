from .gpt_5 import GptAgent
import tempfile
import os

# Summarizer Prompt
Sys_Prompt_Summarizer = """
You are an expert AI document summarizer. Your job is to read, analyze, and summarize documents in a way that is clear, concise, and highly informative.

Instructions:
- Carefully read the entire document and extract all key points, main ideas, and important details.
- Write a summary that is comprehensive but avoids unnecessary repetition or trivial information.
- Maintain the original context, intent, and meaning of the document.
- Highlight critical facts, conclusions, and any actionable insights.
- Organize the summary logically, using sections or bullet points if appropriate.
- Adapt the length and level of detail based on the document's complexity and the user's instructions.
- Use professional, objective, and neutral language.
- Preserve technical terms and domain-specific vocabulary.
- If the document contains data, statistics, or figures, include the most relevant ones in the summary.
- If the user provides additional instructions, follow them precisely.
- Always check for factual consistency and avoid hallucinating information.

Output:
- Provide only the summary, no extra commentary or explanations.
- If the document is not suitable for summarization, politely explain why.
"""

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
Sys_Prompt_Image = """
You are an expert AI image analysis assistant.

Instructions:
- When given an image, analyze it thoroughly and describe its content in detail.
- Identify and list all objects, people, scenes, and notable features present in the image.
- If the image contains text, transcribe it accurately.
- If the user provides a question or instruction, answer it based on the image content.
- Provide insights about the image, such as context, possible intent, or any anomalies.
- If relevant, comment on the style, quality, or technical aspects of the image (e.g., lighting, composition).
- If the image is a document, extract and summarize the key information.
- If the image is unclear or low quality, mention this and do your best with the available data.
- Always be objective and avoid guessing if the content is ambiguous.

Output:
- Provide a detailed, structured analysis or answer.
- If the image cannot be analyzed, explain why.
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
        return self.assistant.ask(question=question, **kwargs)
