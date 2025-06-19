import os
from newberryai.health_chat import HealthChat
from typing import Optional

Sys_Prompt = """

You are an expert in analyzing hospital documents. Extract all key data from this document into a structured JSON format.

First, detect whether this is a MEDICAL BILL or an INVENTORY DOCUMENT, then extract data accordingly.

If it's a MEDICAL BILL, extract these fields:
{
  "documentType": "MedicalBill",
  "billingInfo": {
    "hospitalName": "",
    "hospitalAddress": "",
    "billingDate": "",
    "invoiceNumber": "",
    "patientName": "",
    "patientId": "",
    "insuranceProvider": ""
  },
  "financialSummary": {
    "totalBilled": "",
    "totalDiscounts": "",
    "insuranceCoverage": "",
    "patientResponsibility": "",
    "paymentDueDate": "",
    "paymentStatus": ""
  },
  "itemizedCharges": [
    {
      "serviceName": "",
      "serviceCode": "",
      "serviceDate": "",
      "unitCost": "",
      "quantity": "",
      "totalCost": ""
    }
  ],
  "insuranceDetails": {
    "providerName": "",
    "claimNumber": "",
    "amountBilled": "",
    "coveragePercentage": "",
    "paymentStatus": ""
  },
  "additionalFees": {
    "taxes": "",
    "miscCharges": ""
  },
  "paymentDetails": {
    "paymentMethods": [],
    "lastPaymentDate": "",
    "remainingBalance": ""
  },
  "notes": {
    "remarks": "",
    "contactDetails": ""
  }
}

If it's an INVENTORY DOCUMENT, extract these fields:
{
  "documentType": "Inventory",
  "facilityInfo": {
    "hospitalName": "",
    "departmentName": "",
    "inventoryDate": "",
    "documentId": ""
  },
  "inventorySummary": {
    "totalItems": "",
    "totalValue": "",
    "inventoryPeriod": "",
    "inventoryStatus": ""
  },
  "items": [
    {
      "itemName": "",
      "itemId": "",
      "category": "",
      "quantity": "",
      "unitPrice": "",
      "totalValue": "",
      "expiryDate": "",
      "location": ""
    }
  ],
  "suppliersInfo": [
    {
      "supplierName": "",
      "supplierContact": "",
      "lastOrderDate": "",
      "itemsSupplied": ""
    }
  ],
  "inventoryMetrics": {
    "lowStockItems": [],
    "expiringItems": [],
    "highValueItems": []
  },
  "notes": {
    "remarks": "",
    "contactPerson": "",
    "nextInventoryDate": ""
  }
}

IMPORTANT INSTRUCTIONS:
1. Determine the document type first and set 'documentType' field accordingly
2. Extract ALL information you can find in the document
3. Use EXACTLY the field names provided above
4. For missing information, use null instead of N/A or empty strings
5. For currency values, include only numeric amounts (no currency symbols)
6. For arrays, if no items exist, return an empty array []
7. Return ONLY the JSON without explanations, notes, or markdown formatting
8. Ensure the output is valid JSON that can be parsed with JSON.parse()
9. If the Service code or any other information is not clearly mentioned in the image then do not show them.
10.For any other information which is extra just given them the tage others and show them.

Return ONLY the JSON output with no additional text before or after it.
Return None if No Image Is Provided 
"""

class Bill_extractor:
    """
    A class for extracting key data from hospital documents using the ChatQA model.
    Focused on image-only processing.
    """

    def __init__(self):
        """Initialize the Bill Extractor with the ChatQA assistant."""
        self.assistant = HealthChat(system_prompt=Sys_Prompt)

    def start_gradio(self):
        """Launch the Gradio interface for the Bill Extractor."""
        self.assistant.launch_gradio(
            title="Extract Key Data from Documents",
            description="Upload a hospital document for automatic analysis. The AI will detect whether it's a MEDICAL BILL or an INVENTORY DOCUMENT and extract data accordingly.",
            input_text_label="Additional instructions (optional)",
            input_files_label="Upload document (required)",
            output_label="Extracted data and analysis"
        )

    def run_cli(self):
        """Run the interactive CLI interface for image analysis."""
        print(f"Document Analysis Tool initialized")
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
                
            print("\nAnalyzing document... ", end="")
            answer = self.analyze_document(user_input)
            print("\nAnalysis:")
            print(answer)

    def analyze_document(self, file_path: str, **kwargs):
        """
        Analyze a document image
        
        Args:
            image_path (str): Path to an image file
            
        Returns:
            str: AI's analysis response
        """
        # Use a default prompt for document analysis
        default_prompt = "Please analyze this document and extract the key information into a structured JSON format. Detect whether this is a MEDICAL BILL or an INVENTORY DOCUMENT, then extract data accordingly."
        return self.assistant.ask(question=default_prompt, file_path=file_path, **kwargs)
  