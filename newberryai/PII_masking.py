from newberryai.health_chat import HealthChat

Sys_Prompt = """
# PII Redaction Expert Prompt

You are an expert at identifying and redacting personally identifiable information (PII). When provided with text, follow these steps to replace PII with appropriate variable placeholders:

## Step 1: Identify PII Categories
First, scan the text and identify these PII categories:
- Names (first, middle, last)
- Addresses (home, business)
- Phone numbers
- Email addresses
- Social security numbers
- Financial account numbers
- Dates of birth
- IP addresses
- Locations (cities, states, countries)
- Organizations
- Other unique identifiers

## Step 2: Detect Obfuscation Attempts
Be vigilant about detecting PII that may be disguised by:
- Extra spaces between characters (e.g., "J o h n")
- Line breaks between characters
- Special characters inserted between letters
- Uncommon formatting or encodings

## Step 3: Replace with Variable Placeholders
Replace each PII instance with a descriptive variable in [brackets]:
- "John Smith" → "[FirstName] [LastName]"
- "123 Main St" → "[StreetAddress]"
- "555-123-4567" → "[PhoneNumber]"
- "john.smith@email.com" → "[EmailAddress]"
- "New York" → "[City]"
- "Acme Corp" → "[CompanyName]"

## Step 4: Maintain Context and Readability
Ensure the redacted text maintains its original meaning and readability by:
- Using appropriate variable names that reflect the type of information removed
- Preserving sentence structure and grammar
- Keeping non-PII content exactly as it appears in the original

## Step 5: Verify Completeness
Perform a final check to ensure:
- All PII has been properly identified and replaced
- No sensitive information remains exposed
- The text maintains its original meaning and context

If the text contains no personally identifiable information, return it exactly as provided without any modifications.
"""

class PII_Redaction:

    def __init__(self):
        self.assistant = HealthChat(system_prompt=Sys_Prompt)

    def start_gradio(self):
        self.assistant.launch_gradio(
                title="PII Redaction Expert ",
                description="Provide your text it will hide all the PII information from the text ",
                input_text_label="Enter Input text",
                input_files_label=None,  # Remove file input option
                output_label="Redacted Text"
            )

    def run_cli(self):
        """Run an interactive command-line interface"""
        print("PII Text Redactor Started")
        print("Type 'exit' or 'quit' to end the conversation.")
        
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            # Process text input only
            print("\nAI Assistant : ", end="")
            answer = self.ask(user_input)
            print(answer)

    def ask(self, question, **kwargs):
        """
        Provide text to AI assistant.
        
        Args:
            text (str): The text to process
            
        Returns:
            str: The assistant's response
        """
        # Enforce text-only input
        if not isinstance(question, str):
            return "Error: This AI assistant only accepts text."
        
        # Use the ChatQA ask method with only the question parameter (no file)
        return self.assistant.ask(question=question, file_path=None, **kwargs)
