import argparse
import sys
from newberryai.health_chat import HealthChat

Sys_Prompt = """
Your task is to analyze the provided Python code snippet, identify any bugs or errors present, and provide a corrected version of the code that resolves these issues. Explain the problems you found in the original code and how your fixes address them. The corrected code should be functional, efficient, and adhere to best practices in Python programming.

Key Focus Areas:
- Comprehensive code analysis
- Identifying potential bugs and improvements
- Providing clear explanations of code issues
- Suggesting best practices and optimizations
- Don't answer unrelated questions
"""

class CodeReviewAssistant:
    """
    A class to provide AI-powered code review and analysis functionality.
    """

    def __init__(self):
        """
        Initialize the Code Review Assistant.
        """
        self.assistant = HealthChat(system_prompt=Sys_Prompt)

    def start_gradio(self):
        """
        Launch a web interface for code review using Gradio.
        """
        self.assistant.launch_gradio(
            title="AI Code Review Assistant",
            description="Analyze and improve your Python code with AI-powered insights",
            input_text_label="Paste your Python code snippet here",
            input_image_label=None,  # Disable image input
            output_label="Code Review and Suggestions"
        )

    def run_cli(self):
        """
        Run an interactive command-line interface for code review.
        """
        print("Code Review AI Assistant initialized")
        print("Type 'exit' or 'quit' to end the conversation.")
        
        while True:
            user_input = input("\nEnter your code snippet (or 'exit'/'quit' to stop): ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            # Process text input
            print("\nAI Assistant: ", end="")
            response = self.analyze_code(user_input)
            print(response)

    def ask(self, code_snippet, **kwargs):
        """
        Analyze the provided code snippet.
        
        Args:
            code_snippet (str): The code to be reviewed
            
        Returns:
            str: The assistant's code review and suggestions
        """
        # Validate input
        if not isinstance(code_snippet, str):
            return "Error: Please provide a valid code snippet as text."
        
        # Use the assistant's analysis method
        return self.assistant.ask(question=code_snippet, image_path=None, **kwargs)


def coder_CLI():
    """
    Command-line interface for the Code Review AI Assistant
    """
    parser = argparse.ArgumentParser(description="AI Code Review Assistant")

    parser.add_argument("--code", "-c", type=str, 
                        help="Provide a code snippet for review")
    parser.add_argument("--gradio", "-g", action="store_true", 
                        help="Launch web interface")
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Run in interactive CLI mode")
    
    args = parser.parse_args()
    
    code_review_assistant = CodeReviewAssistant()
    
    if args.gradio:
        print("Launching web interface for Code Review AI Assistant")
        code_review_assistant.start_gradio()
    elif args.interactive:
        print("Starting interactive code review session")
        code_review_assistant.run_interactive_cli()
    elif args.code:
        print(f"Code Snippet: {args.code}\n")
        response = code_review_assistant.ask(args.code)
        print("Code Review:")
        print(response)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    coder_CLI()