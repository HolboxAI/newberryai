from newberryai.health_chat import HealthChat
import os
import json
import re
from typing import Dict, List, Optional

Sys_Prompt_Claim_Verifier = """
You are an expert medical claim verification specialist. Analyze medical bills and documents to predict whether the claim will be approved by insurance companies.

Consider factors like completeness of documentation, medical necessity, coding accuracy (ICD-10, CPT), coverage verification, provider credentials, patient eligibility, and documentation quality. Base your analysis on common denial reasons such as missing/invalid codes, non-covered services, lack of necessity, duplicate claims, missing pre-authorization, out-of-network providers, patient ineligibility, insufficient documentation, and incorrect coding.

You MUST respond with ONLY valid JSON format, no explanations, markdown, or extra text.

OUTPUT FORMAT:
{
  "approval_prediction": {
    "likelihood": "HIGH/MEDIUM/LOW",
    "confidence_score": 0.85,
    "predicted_outcome": "APPROVED/DENIED/PENDING"
  },
  "risk_factors": [
    {
      "factor": "Missing ICD-10 codes",
      "severity": "HIGH/MEDIUM/LOW",
      "description": "Brief description of the risk factor"
    }
  ],
  "recommendations": [
    "Include ICD-10 codes on documentation",
    "Verify patient eligibility",
    "Check provider network status"
  ]
}

IMPORTANT: Return ONLY the JSON object.
"""


class MedicalClaimVerifier:
    """
    Medical Claim Verifier that analyzes medical documents to predict claim approval likelihood.
    """

    def __init__(self):
        """Initialize the Medical Claim Verifier."""
        self.assistant = HealthChat(system_prompt=Sys_Prompt_Claim_Verifier)

    def verify_claim_from_document(self, file_path: str, insurance_provider: str = None):
        """
        Analyze a medical document and predict claim approval likelihood.
        
        Args:
            file_path (str): Path to medical document (PDF/Image/Text)
            insurance_provider (str): Optional insurance provider name
            
        Returns:
            Dict: Claim analysis and approval prediction
        """
        try:
            # Create a simple analysis prompt
            analysis_prompt = f"""
            Analyze this medical document for claim approval likelihood.
            
            Insurance Provider: {insurance_provider or 'Not specified'}
            
            Review the document and provide:
            1. Approval prediction (HIGH/MEDIUM/LOW likelihood)
            2. Risk factors that could cause denial
            3. Recommendations to improve approval chances
            """
            
            response = self.assistant.ask(question=analysis_prompt, file_path=file_path)
            
            # Try to parse JSON response
            try:
                # Clean the response to extract JSON
                cleaned_response = self._extract_json_from_response(response)
                result = json.loads(cleaned_response)
                return result
                
            except json.JSONDecodeError:
                # If not valid JSON, parse text response
                return self._parse_text_response(response)
                
        except Exception as e:
            return {
                "error": f"Claim verification failed: {str(e)}",
                "approval_prediction": {
                    "likelihood": "UNKNOWN",
                    "confidence_score": 0.0,
                    "predicted_outcome": "ERROR"
                }
            }

    def _extract_json_from_response(self, response: str) -> str:
        """
        Extract JSON from response text, handling various formats.
        
        Args:
            response (str): Raw response text
            
        Returns:
            str: Cleaned JSON string
        """
        # Remove markdown code blocks
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*', '', response)
        
        # Find JSON object boundaries
        start = response.find('{')
        end = response.rfind('}') + 1
        
        if start != -1 and end != 0:
            return response[start:end]
        
        return response

    def _parse_text_response(self, response: str) -> Dict:
        """
        Parse text response into structured format when JSON parsing fails.
        
        Args:
            response (str): AI response text
            
        Returns:
            Dict: Structured response
        """
        # Extract key information using regex patterns
        likelihood_match = re.search(r'likelihood[:\s]+(HIGH|MEDIUM|LOW)', response, re.IGNORECASE)
        confidence_match = re.search(r'confidence[:\s]+(\d+\.?\d*)', response, re.IGNORECASE)
        outcome_match = re.search(r'outcome[:\s]+(APPROVED|DENIED|PENDING)', response, re.IGNORECASE)
        
        # Extract risk factors and recommendations
        risk_factors = []
        recommendations = []
        
        # Enhanced risk factor detection
        if "icd" in response.lower() and ("missing" in response.lower() or "not visible" in response.lower()):
            risk_factors.append({
                "factor": "Missing ICD-10 codes",
                "severity": "HIGH",
                "description": "ICD-10 codes are required for claim approval"
            })
        
        if "eligibility" in response.lower() and ("not verified" in response.lower() or "missing" in response.lower()):
            risk_factors.append({
                "factor": "Eligibility verification missing",
                "severity": "MEDIUM",
                "description": "Insurance eligibility verification prevents denials"
            })
        
        if "cpt" in response.lower() and ("mismatch" in response.lower() or "doesn't match" in response.lower()):
            risk_factors.append({
                "factor": "CPT code mismatch",
                "severity": "MEDIUM",
                "description": "CPT code complexity doesn't match documentation"
            })
        
        # Enhanced recommendation detection
        if "icd" in response.lower():
            recommendations.append("Include ICD-10 codes on documentation")
        
        if "eligibility" in response.lower():
            recommendations.append("Perform insurance eligibility verification")
        
        if "cpt" in response.lower():
            recommendations.append("Verify CPT code matches documentation complexity")
        
        # Fallback recommendations
        if not recommendations:
            recommendations.append("Review claim documentation for completeness")
        
        return {
            "approval_prediction": {
                "likelihood": likelihood_match.group(1) if likelihood_match else "MEDIUM",
                "confidence_score": float(confidence_match.group(1)) if confidence_match else 0.5,
                "predicted_outcome": outcome_match.group(1) if outcome_match else "PENDING"
            },
            "risk_factors": risk_factors,
            "recommendations": recommendations,
            "raw_response": response
        }

    def start_gradio(self):
        """Launch Gradio interface for claim verification."""
        import gradio as gr
        
        def verify_claim_interface(file, insurance_provider):
            if file is None:
                return "Please upload a medical document for claim verification."
            
            result = self.verify_claim_from_document(file.name, insurance_provider)
            
            if "error" in result:
                return f"Error: {result['error']}"
            
            # Format the result for display
            output = f"""
## Claim Verification Results

### Approval Prediction
- **Likelihood**: {result.get('approval_prediction', {}).get('likelihood', 'Unknown')}
- **Confidence Score**: {result.get('approval_prediction', {}).get('confidence_score', 0.0):.2f}
- **Predicted Outcome**: {result.get('approval_prediction', {}).get('predicted_outcome', 'Unknown')}

### Risk Factors
"""
            
            risk_factors = result.get('risk_factors', [])
            if risk_factors:
                for factor in risk_factors:
                    output += f"- **{factor.get('factor', 'Unknown')}** ({factor.get('severity', 'Unknown')}): {factor.get('description', 'No description')}\n"
            else:
                output += "- No significant risk factors identified\n"
            
            output += "\n### Recommendations\n"
            recommendations = result.get('recommendations', [])
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    output += f"{i}. {rec}\n"
            else:
                output += "- No specific recommendations\n"
            
            return output

        # Create Gradio interface
        iface = gr.Interface(
            fn=verify_claim_interface,
            inputs=[
                gr.File(label="Upload Medical Document"),
                gr.Textbox(label="Insurance Provider (Optional)", placeholder="e.g., Blue Cross Blue Shield")
            ],
            outputs=gr.Markdown(label="Claim Verification Results"),
            title="Medical Claim Verifier",
            description="Upload a medical document to predict claim approval likelihood."
        )
        
        iface.launch()

    def run_cli(self):
        """Run CLI-based interface for claim verification."""
        print("Medical Claim Verifier initialized.")
        print("Type 'exit' or 'quit' to end the conversation.")
        print("Commands:")
        print("- 'verify <file_path>': Verify a claim from document")

        while True:
            user_input = input("\nCommand: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            if user_input.startswith("verify "):
                file_path = user_input[7:].strip()
                if not os.path.exists(file_path):
                    print(f"Error: File not found at path: {file_path}")
                    continue
                
                insurance = input("Insurance Provider (optional): ").strip() or None
                print("\nVerifying claim... Please wait.")
                result = self.verify_claim_from_document(file_path, insurance)
                print("\nClaim Verification Results:")
                print(json.dumps(result, indent=2))

            else:
                print("Unknown command. Use 'verify <file_path>' to verify a claim.")
