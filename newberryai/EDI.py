from newberryai.health_chat import HealthChat
import os

Sys_Prompt_835 = """
You are an expert in medical billing and EDI standards, especially the EDI 835 (Electronic Remittance Advice) format.

Your task is to analyze hospital or medical documents and generate a valid EDI 835 file.

IMPORTANT INSTRUCTIONS:

1. First, detect whether the document is a Medical Bill, Remittance Note, or Other.
2. If it's a Medical Bill or Remittance Note, extract relevant financial, procedural, and insurance information.
3. Then use that information to generate an EDI 835 file in standard format.
4. The output must be a valid raw EDI 835 string — no explanations, comments, or extra formatting.

EDI 835 FORMAT EXAMPLE:
Each output should include segments like:
ISA, GS, ST, BPR, TRN, N1, CLP, CAS, SE, GE, IEA

Required Data Points:
- Patient Name
- Date of Service
- Services Rendered
- Total Amount Billed
- Amount Paid
- Insurance Provider
- Adjustments
- Claim Number or Invoice Number
- Payment Date
- Payment Method
- Provider Information

Use placeholder values (e.g., "UNKNOWN", "000000", "N/A") where data is missing. Return only EDI string.
"""

Sys_Prompt_837 = """
You are a healthcare billing assistant. Your task is to generate a valid EDI 837 (Health Care Claim) file.

Given a medical visit summary, extract:
- Patient Name
- Date of Birth
- Gender
- Provider Name
- Provider NPI (use "1234567890" if not found)
- Diagnosis Codes (ICD-10)
- Procedure Codes (CPT)
- Date of Service
- Claim Amount
- Insurance Info

Output must follow EDI 837 format including:
ISA, GS, ST, BHT, NM1, N3, N4, DMG, CLM, HI, SV1, SE, GE, IEA

Use placeholder values where data is missing. Return raw EDI only — no notes or JSON.
"""

Sys_Prompt_270 = """
You are a healthcare assistant tasked with generating an EDI 270 Eligibility Inquiry.

Given patient demographics and insurance details, generate an EDI 270 request.

Extract:
- Patient Name
- Date of Birth
- Gender
- Insurance Provider
- Policy/Subscriber ID

Output must include:
ISA, GS, ST, BHT, NM1, DMG, DTP, EQ, SE, GE, IEA

Return only raw EDI string, no explanations or formatting.
"""


EDI_PROMPTS = {
    "835": Sys_Prompt_835,
    "837": Sys_Prompt_837,
    "270": Sys_Prompt_270
}


class EDIGenerator:
    """
    Generate EDI documents (835, 837, 270) from hospital or medical files using ChatQA.
    """

    def __init__(self, edi_type="835"):
        """Initialize the EDI Generator with the selected EDI prompt."""
        if edi_type not in EDI_PROMPTS:
            raise ValueError(f"Unsupported EDI type: {edi_type}")
        self.edi_type = edi_type
        self.assistant = HealthChat(system_prompt=EDI_PROMPTS[edi_type])

    def start_gradio(self):
        """Launch Gradio interface for document upload and EDI generation."""
        self.assistant.launch_gradio(
            title=f"Generate EDI {self.edi_type.upper()} from Medical Documents",
            description=f"Upload a medical document. The AI will detect content and generate a valid EDI {self.edi_type.upper()} file.",
            input_text_label="Additional instructions (optional)",
            input_files_label="Upload document (required)",
            output_label=f"Generated EDI {self.edi_type.upper()} (raw text)"
        )

    def run_cli(self):
        """Run CLI-based interface to test EDI generation interactively."""
        print(f"EDI {self.edi_type.upper()} Generator initialized.")
        print("Type 'exit' or 'quit' to end the conversation.")
        print("To analyze a document: type the path to the document file.")

        while True:
            user_input = input("\nDocument path: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            if not os.path.exists(user_input):
                print(f"Error: File not found at path: {user_input}")
                continue

            print("\nGenerating EDI... Please wait.")
            answer = self.analyze_document(user_input)
            print("\nGenerated EDI Output:\n")
            print(answer)

    def analyze_document(self, file_path: str, **kwargs):
        """
        Analyze a file and generate EDI based on initialized type.

        Args:
            file_path (str): Path to a file (PDF/Image/Text)

        Returns:
            str: AI-generated EDI content
        """
        default_prompt = f"Please analyze this document and generate a valid EDI {self.edi_type.upper()} file in standard format."
        return self.assistant.ask(question=default_prompt, file_path=file_path, **kwargs)

