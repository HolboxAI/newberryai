from newberryai.health_chat import HealthChat

Sys_Prompt = """
You are an expert medical coder specializing in ICD-10 and CPT coding. 
Your task is to read the following medical bill/doctor's note and return a structured list of medical codes. 

### Instructions:
1. Extract all diagnoses, procedures, and treatments from the input text.  
2. Map diagnoses to **ICD-10 codes** with description.  
3. Map procedures/services to **CPT codes** with description.  
4. If multiple codes apply, list them all as separate objects in an array.  
5. If uncertain, insert "Needs human review" in the code and description fields instead of guessing.  
6. Always return the output strictly in **valid JSON format only** with the following fields:  
   - diagnosis  
   - icd10_code  
   - icd10_description  
   - procedure  
   - cpt_code  
   - cpt_description  
7. If a field is not applicable, use **null** instead of an empty string.   

### Input Text (medical bill/doctor's note):
{INSERT_MEDICAL_TEXT_HERE}

### Output:
[
  {
    "diagnosis": "",
    "icd10_code": "",
    "icd10_description": "",
    "procedure": "",
    "cpt_code": "",
    "cpt_description": ""
  }
]

"""

class MedicalCoder:
    """
    A class to provide AI-powered medical coding for ICD-10 and CPT codes.
    """

    def __init__(self):
        """
        Initialize the medical coding Assistant.
        """
        self.assistant = HealthChat(system_prompt=Sys_Prompt)

    def start_gradio(self):
        """
        Launch a web interface for medical coding using Gradio.
        """
        self.assistant.launch_gradio(
            title="Medical Coding Assistant",
            description="Extract ICD-10 and CPT codes from medical documents",
            input_text_label="Medical text or additional instructions (optional)",
            input_files_label="Upload medical document (required)",
            output_label="Medical Codes"
        )

    def run_cli(self):
        """
        Run an interactive command-line interface for medical coding.
        """
        print("Medical Coding AI Assistant initialized")
        print("Type 'exit' or 'quit' to end the conversation.")
        
        while True:
            user_input = input("\nEnter your medical document path or text: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            # Process text input
            print("\nAI Assistant: ", end="")
            response = self.ask(user_input)
            print(response)

    def ask(self, file_path, **kwargs):
        """
        Extract medical codes from the provided document or text.
        
        Args:
            file_path (str): Path to the medical document or medical text to be coded
            
        Returns:
            str: The assistant's medical coding result in JSON format
        """
        # Validate input
        if not isinstance(file_path, str):
            return "Error: Please provide a valid document path or medical text."
        
        return self.assistant.ask(file_path=file_path, **kwargs)
