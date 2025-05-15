import argparse
import sys
from newberryai.health_chat import HealthChat

Sys_Prompt = """
# PII Extraction Expert Prompt

You are an expert at identifying and extracting personally identifiable information (PII). When provided with text, extract all PII and return it in a simple JSON format.

## Step 1: Identify PII Categories
Scan the text thoroughly to identify these PII categories:
- Names (first, middle, last names of people)
- Addresses (physical locations where someone lives or works)
- Phone numbers (any format including international)
- Email addresses
- Social security numbers and government IDs
- Financial information (account numbers, credit cards)
- Dates of birth
- IP addresses
- Locations (cities, states, countries)
- Organizations and companies
- Other unique identifiers

## Step 2: Watch for Disguised PII
Be vigilant about PII that may be hidden through:
- Spaced characters (e.g., "J o h n")
- Line breaks between characters
- Special characters inserted between letters

## Step 3: Extract All PII
For each PII instance found, extract it completely and assign to the appropriate category.

## Step 4: Return Simple JSON
Format all extracted PII in a clean JSON with straightforward key-value pairs:

```json
{
  "Name": "John Smith",
  "PhoneNumber": "555-123-4567",
  "Email": "john.smith@email.com",
  "Address": "123 Main St, Anytown, ST 12345",
  "Location": "New York",
  "Organization": "Acme Corp",
  "DOB": "01/15/1980",
  "SSN": "123-45-6789"
}
```

## Step 5: Final Check
Verify that all PII has been extracted and properly categorized. Return an empty object {} if no PII is found.

## Learning Examples:

Example 1:
Input: "My name is John Doe and I live in Boston."
Output: {"Name": "John Doe", "Location": "Boston"}

Example 2:
Input: "Contact me at user@example.com or call 555-123-4567"
Output: {"Email": "user@example.com", "PhoneNumber": "555-123-4567"}

Example 3:
Input: "Sarah J. Williams works at ABC Corp in New York City."
Output: {"Name": "Sarah J. Williams", "Organization": "ABC Corp", "Location": "New York City"}

"""
class PII_extraction:

    def __init__(self):
        self.assistant = HealthChat(system_prompt=Sys_Prompt)

    def start_gradio(self):
        self.assistant.launch_gradio(
                title="PII extraction Expert ",
                description="Provide your text it will extract all the PII information from the text ",
                input_text_label="Enter Input text",
                input_image_label=None,  # Remove image input option
                output_label="extracted Text"
            )

    def run_cli(self):
        """Run an interactive command-line interface"""
        print("PII Text extractor Started")
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
        
        # Use the ChatQA ask method with only the question parameter (no image)
        return self.assistant.ask(question=question, image_path=None, **kwargs)


def PII_extractor_CLI():
    """Command-line interface for the AI Assistant"""
    parser = argparse.ArgumentParser(description="PII AI Assistant")

    parser.add_argument("--text", "-t", type=str, help="The text for PII extraction AI Assistant")
    parser.add_argument("--gradio", "-g", action="store_true", 
                        help="Launch Gradio interface")
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Run in interactive CLI mode")
    
    args = parser.parse_args()
    
    pii_extract = PII_extraction()
    
    if args.gradio:
        print("Launching Gradio interface for AI Assistant")
        pii_extract.start_gradio()
    elif args.interactive:
        print("Starting interactive session for AI Assistant")
        pii_extract.run_cli()
    elif args.question:
        print(f"Question: {args.question}\n")
        response = pii_extract.ask(args.question)
        print("Response:")
        print(response)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    PII_extractor_CLI()