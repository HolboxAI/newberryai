from newberryai.health_chat import HealthChat

Sys_Prompt = """
As an Excel Formula Expert, your task is to provide advanced Excel formulas that perform the complex calculations or data manipulations described by the user. If the user does not provide this information, ask the user to describe the desired outcome or operation they want to perform in Excel. Make sure to gather all the necessary information you need to write a complete formula, such as the relevant cell ranges, specific conditions, multiple criteria, or desired output format. Once you have a clear understanding of the user’s requirements, provide a detailed explanation of the Excel formula that would achieve the desired result. Break down the formula into its components, explaining the purpose and function of each part and how they work together. Additionally, provide any necessary context or tips for using the formula effectively within an Excel worksheet.

Key Focus Areas:
- Comprehensive formula creation
- Clear, technical explanation
- Practical guidance
- Don't Answer unrelated topics
"""

class ExcelExp:

    def __init__(self):
        self.assistant = HealthChat(system_prompt=Sys_Prompt)

    def start_gradio(self):
        self.assistant.launch_gradio(
                title="Excel Formula AI Assistant",
                description="The toolkit offers flexibility in approaching Excel formula challenges, with structured methods ",
                input_text_label="Enter problem, data range, conditions, and notes Here ",
                input_files_label=None,  # Remove file input option
                output_label="Excel Formula"
            )

    def run_cli(self):
        """Run an interactive command-line interface"""
        print("AI Assistant initialized")
        print("Type 'exit' or 'quit' to end the conversation.")
        
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            # Process text input only
            print("Assistant: ", end="")
            answer = self.ask(user_input)
            print(answer)

    def ask(self, question, **kwargs):
        """
        Ask a question to the AI assistant.
        
        Args:
            question (str): The question to process
            
        Returns:
            str: The assistant's response
        """
        # Enforce text-only input
        if not isinstance(question, str):
            return "Error: This AI assistant only accepts text questions."
        
        # Use the ChatQA ask method with only the question parameter (no file)
        return self.assistant.ask(question=question, file_path=None, **kwargs)
