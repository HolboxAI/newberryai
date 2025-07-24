from newberryai.health_chat import HealthChat
import os

Sys_Prompt = """
You are an expert in medical billing and EDI standards, especially the EDI 835 (Electronic Remittance Advice) format.

Your task is to analyze hospital or medical documents and generate a valid EDI 835 file.

IMPORTANT INSTRUCTIONS:

1. First, detect whether the document is a **Medical Bill**, **Remittance Note**, or **Other**.
2. If it's a Medical Bill or Remittance Note, extract relevant financial, procedural, and insurance information.
3. Then use that information to generate an EDI 835 file in standard format.
4. The output must be a valid raw EDI 835 string — no explanations, comments, or extra formatting.

EDI 835 FORMAT EXAMPLE:
Each output should include segments like:
ISA, GS, ST, BPR, TRN, N1, CLP, CAS, SE, GE, IEA

Required Data Points:
- Patient Name
- Date of Service
- Services Rendered (with descriptions and codes if available)
- Total Amount Billed
- Amount Paid
- Insurance Provider
- Adjustments (if any)
- Claim Number or Invoice Number
- Payment Date
- Payment Method
- Provider Information (Hospital/Clinic Name)

STRICT RULES:
- If data is missing in the input, use placeholder values (e.g., "UNKNOWN", "000000", "N/A") in the EDI.
- You must still return a structurally valid EDI 835.
- DO NOT return JSON, markdown, or explanation — return only plain EDI text.
- Output should be ready to save as `.edi` or `.txt`.

Example Input (Medical Doc):
Patient: John Doe
Date of Service: July 12, 2025
Diagnosis: Acute bronchitis
Procedure: Office visit, chest X-ray
Total Charge: $250
Paid Amount: $200
Insurance Provider: Blue Cross
Adjustment Reason: Contractual Obligation
Claim Number: 12345678
Payment Date: July 20, 2025

Now generate the EDI 835 for this input.

If no medical content is provided, return only the word: "None".
"""

class EDI835Extractor:
    """
    A class for generating EDI 835 files from hospital or medical documents using the ChatQA model.
    Focused on image and document processing for EDI output.
    """

    def __init__(self):
        """Initialize the EDI 835 Extractor with the ChatQA assistant."""
        self.assistant = HealthChat(system_prompt=Sys_Prompt)

    def start_gradio(self):
        """Launch the Gradio interface for the EDI 835 Extractor."""
        self.assistant.launch_gradio(
            title="Generate EDI 835 from Medical Documents",
            description="Upload a hospital or medical document. The AI will detect the type and generate a valid EDI 835 file.",
            input_text_label="Additional instructions (optional)",
            input_files_label="Upload document (required)",
            output_label="Generated EDI 835 (raw text)"
        )

    def run_cli(self):
        """Run the interactive CLI interface for EDI 835 generation."""
        print(f"EDI 835 Generator initialized")
        print("Type 'exit' or 'quit' to end the conversation.")
        print("To analyze a document: type the path to the document file")
        
        while True:
            user_input = input("\nDocument path: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            if not os.path.exists(user_input):
                print(f"Error: File not found at path: {user_input}")
                continue
                
            print("\nGenerating EDI 835... ", end="")
            answer = self.analyze_document(user_input)
            print("\nEDI 835 Output:")
            print(answer)

    def analyze_document(self, file_path: str, **kwargs):
        """
        Analyze a document and generate an EDI 835 file
        
        Args:
            file_path (str): Path to an image or document file
            
        Returns:
            str: AI's EDI 835 response
        """
        default_prompt = "Please analyze this document and generate a valid EDI 835 file in standard format."
        return self.assistant.ask(question=default_prompt, file_path=file_path, **kwargs)
