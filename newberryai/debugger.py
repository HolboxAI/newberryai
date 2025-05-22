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
            input_files_label=None,  # Disable file input
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
        return self.assistant.ask(question=code_snippet, file_path=None, **kwargs)
    