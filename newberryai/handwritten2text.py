from newberryai.health_chat import HealthChat

Sys_Prompt = """
You are an expert at reading and transcribing handwritten documents.
Extract all handwritten text from the uploaded image and return it as plain, machine-readable digital text.
Do not include any explanations, formatting, or extra commentary—just the raw transcribed text. 
If the image does not contain any handwritten text, return an empty string.
If no image is provided, return None.
"""

class Handwrite2Text:
    """
    A class for converting handwritten document images to digital text using the HealthChat model.
    """
    def __init__(self):
        self.assistant = HealthChat(system_prompt=Sys_Prompt)

    def start_gradio(self):
        self.assistant.launch_gradio(
            title="Handwriting to Text Converter",
            description="Upload an image of a handwritten document to extract and digitize the text.",
            input_text_label="Additional instructions (optional)",
            input_files_label="Upload handwritten document image (required)",
            output_label="Extracted Digital Text"
        )

    def run_cli(self):
        print("Handwriting to Text Converter initialized")
        print("Type 'exit' or 'quit' to end the conversation.")
        print("To convert handwriting: type the path to the image file")
        while True:
            user_input = input("\nImage path: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            if not user_input or not isinstance(user_input, str):
                print("Error: Please provide a valid image file path.")
                continue
            import os
            if not os.path.exists(user_input):
                print(f"Error: File not found at path: {user_input}")
                continue
            print("\nExtracting text... ", end="")
            answer = self.extract_text(user_input)
            print("\nExtracted Text:")
            print(answer)

    def extract_text(self, file_path: str, **kwargs):
        prompt = "Extract all handwritten text from this image and return it as plain digital text."
        return self.assistant.ask(question=prompt, file_path=file_path, **kwargs)
