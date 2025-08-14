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

EDI 835 FORMAT REQUIREMENTS:

REQUIRED SEGMENTS (in order):
ISA*00*          *00*          *ZZ*SENDER_ID     *ZZ*RECEIVER_ID   *YYMMDD*HHMM*U*00401*000000001*0*P*>~
GS*HP*SENDER_ID*RECEIVER_ID*YYMMDD*HHMM*1*X*005010X221A1~
ST*835*0001~
BPR*D*150.00*C*ACH*CTX*01*123456789*DA*987654321*1234567890123456*DA*987654321*1234567890123456*20241201~
TRN*1*123456789012345*987654321~
DTM*405*20241201~
N1*PR*INSURANCE_PROVIDER_NAME~
N3*PROVIDER_ADDRESS~
N4*CITY*ST*ZIPCODE~
CLM*CLAIM_NUMBER*150.00*1***11:A:1~
CAS*CO*45*50.00~
CAS*PR*1*100.00~
SE*8*0001~
GE*1*1~
IEA*1*000000001~

CRITICAL REQUIREMENTS:
- Use real bank routing numbers (9 digits) and account numbers (variable length)
- TRN02 must be a real payment trace number (15 digits)
- TRN03 must be the correct payer bank routing number (9 digits)
- Include DTM*405 segment for payment date
- Use actual trading partner IDs (SENDER_ID, RECEIVER_ID) instead of placeholders
- Ensure ISA control number matches IEA control number
- Use incrementing control numbers (0001, 0002, etc.)
- All dates in CCYYMMDD format
- All monetary values in two-decimal format (e.g., 150.00)
- Include complete ACH/CCP payment details in BPR segment
 
FORMATTING RULES:
- All dates must be in CCYYMMDD format
- All monetary values must have two decimal places (e.g., 150.00)
- Ensure ISA control number matches IEA control number, GS matches GE
- Use incrementing control numbers (0001, 0002, etc. for ST/SE; 000000001, 000000002, etc. for ISA/IEA)
- Use actual trading partner IDs (SENDER_ID, RECEIVER_ID)
- Use valid bank routing numbers (9 digits) and account numbers (variable length where applicable)
- Return only the raw EDI string with proper segment terminators (~)

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

EDI 837 FORMAT REQUIREMENTS:

REQUIRED SEGMENTS (in order):
ISA*00*          *00*          *ZZ*SENDER_ID     *ZZ*RECEIVER_ID   *YYMMDD*HHMM*U*00401*000000002*0*P*>~
GS*HC*SENDER_ID*RECEIVER_ID*YYMMDD*HHMM*2*X*005010X222A1~
ST*837*0001~
BHT*0019*00*123456789012345*20241201*120000*CH~
NM1*41*2*SUBMITTER_NAME*****46*SUBMITTER_ID~
PER*IC*CONTACT_NAME*TE*PHONE~
NM1*40*2*INSURANCE_NAME*****46*INSURANCE_ID~
NM1*85*2*PROVIDER_NAME*****XX*PROVIDER_NPI~
N3*PROVIDER_ADDRESS~
N4*CITY*ST*ZIPCODE-EXTENSION~
NM1*QC*1*PATIENT_LAST*PATIENT_FIRST~
DMG*D8*YYYYMMDD*F~
CLM*CLAIM_NUMBER*CLAIM_AMOUNT*1***11:A:1*Y*A*Y*Y~
DTP*434*D8*STATEMENT_DATE~
DTP*472*D8*SERVICE_DATE~
HI*BK:ICD10_CODE~
SV1*1*CPT_CODE*CLAIM_AMOUNT*UN*1*50.00*50.00~
SE*15*0001~
GE*1*2~
IEA*1*000000002~

CRITICAL REQUIREMENTS:
- Use actual billing service info for NM1*41 (submitter) and keep NM1*85 as billing provider
- Change ZIP codes from 5-digit to 9-digit format (12345-6789) where possible
- In CLM segment, add claim frequency code (CLM05-3) if available
- Add DTP*434 segment for statement date in addition to service date
- Use actual trading partner IDs (SENDER_ID, RECEIVER_ID)
- Ensure ISA control number matches IEA control number, GS matches GE
- Use incrementing control numbers (000000002, 000000003, etc.)
- All dates in CCYYMMDD format
- All monetary values in two-decimal format (e.g., 150.00)

FORMATTING RULES:
- All dates must be in CCYYMMDD format
- All monetary values must have two decimal places (e.g., 150.00)
- Ensure ISA control number matches IEA control number, GS matches GE
- Use incrementing control numbers (0001, 0002, etc. for ST/SE; 000000001, 000000002, etc. for ISA/IEA)
- Use actual trading partner IDs (SENDER_ID, RECEIVER_ID)
- Use valid bank routing numbers (9 digits) and account numbers (variable length where applicable)
- Return only the raw EDI string with proper segment terminators (~)
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

EDI 270 FORMAT REQUIREMENTS:

REQUIRED SEGMENTS (in order):
ISA*00*          *00*          *ZZ*SENDER_ID     *ZZ*RECEIVER_ID   *YYMMDD*HHMM*U*00401*000000003*0*P*>~
GS*HS*SENDER_ID*RECEIVER_ID*YYMMDD*HHMM*3*X*005010X279A1~
ST*270*0001~
BHT*0022*13*123456789012345*20241201*120000*RT~
HL*1**20*1~
NM1*PR*2*INSURANCE_NAME*****PI*INSURANCE_ID~
NM1*1P*2*PROVIDER_NAME*****XX*PROVIDER_NPI~
HL*2*1*21*1~
NM1*IL*1*SUBSCRIBER_LAST*SUBSCRIBER_FIRST~
DMG*D8*YYYYMMDD*F~
DTP*307*D8*ELIGIBILITY_START_DATE~
DTP*472*D8*SERVICE_DATE~
EQ*30~
SE*12*0001~
GE*1*3~
IEA*1*000000003~

CRITICAL REQUIREMENTS:
- Expand EQ segment to include specific service type codes (e.g., 30 for office visit, 35 for consultation)
- Add DTP*307 (eligibility start date) and DTP*472 (service date) in addition to inquiry date
- Use actual trading partner IDs (SENDER_ID, RECEIVER_ID)
- Ensure ISA control number matches IEA control number, GS matches GE
- Use incrementing control numbers (000000003, 000000004, etc.)
- All dates in CCYYMMDD format
- Include relevant service type codes in EQ segment

FORMATTING RULES:
- All dates must be in CCYYMMDD format
- All monetary values must have two decimal places (e.g., 150.00)
- Ensure ISA control number matches IEA control number, GS matches GE
- Use incrementing control numbers (0001, 0002, etc. for ST/SE; 000000001, 000000002, etc. for ISA/IEA)
- Use actual trading partner IDs (SENDER_ID, RECEIVER_ID)
- Use valid bank routing numbers (9 digits) and account numbers (variable length where applicable)
- Return only the raw EDI string with proper segment terminators (~)`
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

