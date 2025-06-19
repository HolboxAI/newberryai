from newberryai.health_chat import HealthChat

Sys_Prompt = """
You are an AI document summarizer assistant. Your task is to analyze and summarize documents provided to you in a clear, concise, and informative manner.

Key Focus Areas:
- Extract key information and main points from the document
- Provide a comprehensive yet concise summary
- Maintain the original context and meaning
- Highlight important details, facts, and conclusions
- Organize information in a logical and coherent structure
- Adapt the summary length and detail level based on the document's complexity
- Ensure accuracy and factual consistency in the summary

Guidelines:
- Focus on the most important information while omitting redundant or trivial details
- Use clear and professional language
- Maintain objectivity in the summary
- Preserve critical technical terms and domain-specific vocabulary
- Structure the summary with appropriate headings and sections when needed
- Provide context when necessary to ensure understanding
"""

class DocSummarizer:
    """
    A class to provide AI-powered document summarization.
    """

    def __init__(self):
        """
        Initialize the document summarizer Assistant.
        """
        self.assistant = HealthChat(system_prompt=Sys_Prompt)

    def start_gradio(self):
        """
        Launch a web interface for document summarizer using Gradio.
        """
        self.assistant.launch_gradio(
            title="Document Summarizer Assistant",
            description="Extract and summarize your document with AI",
            input_text_label="Additional instructions (optional)",
            input_files_label= "Upload document (required)",
            output_label="Summary"
        )

    def run_cli(self):
        """
        Run an interactive command-line interface for document summarizer.
        """
        print("Document Summarizer AI Assistant initialized")
        print("Type 'exit' or 'quit' to end the conversation.")
        
        while True:
            user_input = input("\nEnter your document path: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            # Process text input
            print("\nAI Assistant: ", end="")
            response = self.ask(user_input)
            print(response)

    def ask(self, file_path, **kwargs):
        """
        Summarize the provided document.
        
        Args:
            doc_path (str): Path to the document to be summarized
            
        Returns:
            str: The assistant's document summary
        """
        # Validate input
        if not isinstance(file_path, str):
            return "Error: Please provide a valid document path."
        
        return self.assistant.ask(file_path=file_path, **kwargs)
