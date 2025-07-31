from newberryai.health_chat import HealthChat
from newberryai.EDI import EDIGenerator
import os
import json
import re
from typing import Dict, List, Optional, Tuple

Sys_Prompt_Claim_Verifier = """
You are an expert medical claim verification specialist. Your task is to analyze EDI 837 claim data and predict whether the claim will be approved by insurance companies.

ANALYSIS CRITERIA:
1. **Claim Completeness**: Missing required fields, incomplete documentation
2. **Medical Necessity**: Whether procedures/services are medically necessary
3. **Coding Accuracy**: Proper ICD-10 and CPT code usage and matching
4. **Coverage Verification**: Whether services are covered under typical policies
5. **Provider Credentials**: Valid provider information
6. **Patient Eligibility**: Correct patient information and eligibility status
7. **Documentation Quality**: Adequate clinical documentation
8. **ICD-10 Documentation**: Ensure ICD-10 codes are visible on image-based bills
9. **CPT Code Validation**: Verify CPT codes match documentation complexity
10. **Eligibility Verification**: Check if eligibility verification was performed

COMMON DENIAL REASONS:
- Missing or invalid diagnosis codes (ICD-10)
- Non-covered services
- Lack of medical necessity
- Duplicate claims
- Missing pre-authorization
- Provider out of network
- Patient not eligible
- Insufficient documentation
- Incorrect coding
- ICD-10 codes not visible on image-based documentation
- CPT codes not matching documentation complexity
- Missing eligibility verification

SPECIFIC VALIDATION POINTS:
- **ICD-10 Codes**: Must be visible on image-based bills, not just in EDI
- **Eligibility Check**: Standard requirement - insurance eligibility verification prevents denials
- **CPT Code Match**: Verify CPT codes (e.g., 99214 for moderate-complexity visits) match documentation

CRITICAL CONSISTENCY CHECKS:
- **EDI-Image Alignment**: Ensure all data in EDI 837 matches what's visible on image documentation
- **ICD-10 Visibility**: ICD-10 codes must be visible on image, not just embedded in EDI
- **CPT Consistency**: CPT codes must match between EDI and image documentation
- **Patient/Provider Info**: All patient and provider details must be consistent
- **Service Dates**: Service dates must match between EDI and image
- **Billed Amounts**: Amounts must be consistent between EDI and image

CRITICAL: You MUST respond with ONLY valid JSON format. No explanations, no markdown, no additional text.

OUTPUT FORMAT:
{
  "approval_prediction": {
    "likelihood": "HIGH/MEDIUM/LOW",
    "confidence_score": 0.85,
    "predicted_outcome": "APPROVED/DENIED/PENDING"
  },
  "risk_factors": [
    {
      "factor": "Missing ICD-10 on image documentation",
      "severity": "HIGH/MEDIUM/LOW",
      "description": "ICD-10 codes must be visible on image-based bills for approval"
    }
  ],
  "recommendations": [
    "Include ICD-10 codes on image-based documentation",
    "Perform insurance eligibility verification",
    "Verify CPT code matches documentation complexity"
  ],
  "validation_checks": {
    "icd10_visible": true/false,
    "eligibility_verified": true/false,
    "cpt_matches_documentation": true/false
  }
}

IMPORTANT: Return ONLY the JSON object, nothing else. No code blocks, no explanations.
"""

class MedicalClaimVerifier:
    """
    Medical Claim Verifier that uses EDI 837 data to predict claim approval likelihood.
    """

    def __init__(self):
        """Initialize the Medical Claim Verifier."""
        self.assistant = HealthChat(system_prompt=Sys_Prompt_Claim_Verifier)
        self.edi_generator = EDIGenerator(edi_type="837")

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
            # Generate EDI 837 from the document using existing EDI.py functionality
            edi_837 = self.edi_generator.analyze_document(file_path)
            
            # Perform consistency check between EDI and image documentation
            consistency_check = self._check_edi_image_consistency(edi_837, file_path)
            
            # Analyze the EDI 837 for approval likelihood
            analysis_prompt = f"""
            Analyze this EDI 837 claim for approval likelihood:
            
            EDI 837 Data:
            {edi_837}
            
            Consistency Check Results:
            {consistency_check}
            
            Insurance Provider: {insurance_provider or 'Not specified'}
            
            Provide approval prediction, risk factors, and recommendations.
            """
            
            response = self.assistant.ask(question=analysis_prompt, file_path=file_path)
            
            # Try to parse JSON response
            try:
                # Clean the response to extract JSON
                cleaned_response = self._extract_json_from_response(response)
                result = json.loads(cleaned_response)
                
                # Add consistency check results to the response
                result['consistency_check'] = consistency_check
                return result
                
            except json.JSONDecodeError:
                # If not valid JSON, try to parse text response
                result = self._parse_text_response(response)
                result['consistency_check'] = consistency_check
                return result
                
        except Exception as e:
            return {
                "error": f"Claim verification failed: {str(e)}",
                "approval_prediction": {
                    "likelihood": "UNKNOWN",
                    "confidence_score": 0.0,
                    "predicted_outcome": "ERROR"
                }
            }

    def _check_edi_image_consistency(self, edi_837_content: str, file_path: str) -> Dict:
        """
        Check consistency between EDI 837 data and image-based documentation.
        
        Args:
            edi_837_content (str): Generated EDI 837 content
            file_path (str): Path to original document
            
        Returns:
            Dict: Consistency check results
        """
        consistency_prompt = """
        Perform a detailed consistency check between EDI 837 data and image-based documentation.
        
        Check for:
        1. **ICD-10 Code Alignment**: Are ICD-10 codes present in both EDI and visible on image?
        2. **CPT Code Alignment**: Are CPT codes consistent between EDI and image documentation?
        3. **Patient Information**: Are patient details consistent across both sources?
        4. **Provider Information**: Are provider details consistent?
        5. **Service Dates**: Are service dates consistent?
        6. **Amounts**: Are billed amounts consistent?
        
        Return detailed consistency analysis with specific mismatches identified.
        """
        
        try:
            response = self.assistant.ask(
                question=f"{consistency_prompt}\n\nEDI 837 Content:\n{edi_837_content}",
                file_path=file_path
            )
            
            # Extract consistency information
            consistency_issues = []
            alignment_score = 1.0
            
            # Check for common consistency issues
            if "icd" in response.lower() and ("missing" in response.lower() or "not visible" in response.lower()):
                consistency_issues.append("ICD-10 codes in EDI but not visible on image documentation")
                alignment_score -= 0.3
            
            if "cpt" in response.lower() and ("mismatch" in response.lower() or "inconsistent" in response.lower()):
                consistency_issues.append("CPT codes inconsistent between EDI and image")
                alignment_score -= 0.2
            
            if "patient" in response.lower() and ("mismatch" in response.lower() or "inconsistent" in response.lower()):
                consistency_issues.append("Patient information inconsistent between EDI and image")
                alignment_score -= 0.2
            
            if "provider" in response.lower() and ("mismatch" in response.lower() or "inconsistent" in response.lower()):
                consistency_issues.append("Provider information inconsistent between EDI and image")
                alignment_score -= 0.1
            
            if "date" in response.lower() and ("mismatch" in response.lower() or "inconsistent" in response.lower()):
                consistency_issues.append("Service dates inconsistent between EDI and image")
                alignment_score -= 0.1
            
            if "amount" in response.lower() and ("mismatch" in response.lower() or "inconsistent" in response.lower()):
                consistency_issues.append("Billed amounts inconsistent between EDI and image")
                alignment_score -= 0.1
            
            return {
                "alignment_score": max(0.0, alignment_score),
                "consistency_issues": consistency_issues,
                "overall_status": "PASS" if alignment_score >= 0.8 else "FAIL" if alignment_score < 0.5 else "WARNING",
                "detailed_analysis": response
            }
            
        except Exception as e:
            return {
                "alignment_score": 0.0,
                "consistency_issues": [f"Consistency check failed: {str(e)}"],
                "overall_status": "ERROR",
                "detailed_analysis": "Consistency check could not be performed"
            }

    def verify_edi_837_claim(self, edi_837_content: str, insurance_provider: str = None):
        """
        Verify an existing EDI 837 claim for approval likelihood.
        
        Args:
            edi_837_content (str): Raw EDI 837 content
            insurance_provider (str): Optional insurance provider name
            
        Returns:
            Dict: Claim analysis and approval prediction
        """
        try:
            analysis_prompt = f"""
            Analyze this EDI 837 claim for approval likelihood:
            
            {edi_837_content}
            
            Insurance Provider: {insurance_provider or 'Not specified'}
            
            Provide approval prediction, risk factors, and recommendations.
            """
            
            response = self.assistant.ask(question=analysis_prompt)
            
            try:
                # Clean the response to extract JSON
                cleaned_response = self._extract_json_from_response(response)
                return json.loads(cleaned_response)
            except json.JSONDecodeError:
                return self._parse_text_response(response)
                
        except Exception as e:
            return {
                "error": f"EDI claim verification failed: {str(e)}",
                "approval_prediction": {
                    "likelihood": "UNKNOWN",
                    "confidence_score": 0.0,
                    "predicted_outcome": "ERROR"
                }
            }

    def validate_specific_requirements(self, file_path: str = None, edi_837_content: str = None):
        """
        Validate the three specific requirements mentioned in recommendations:
        1. ICD-10 codes visible on image-based bills
        2. Eligibility verification performed
        3. CPT code matches documentation complexity
        
        Args:
            file_path (str): Path to medical document (if available)
            edi_837_content (str): EDI 837 content (if available)
            
        Returns:
            Dict: Specific validation results
        """
        validation_prompt = """
        Perform specific validation checks on this medical claim:
        
        1. **ICD-10 Documentation Check**: Verify that ICD-10 codes are visible on image-based documentation, not just in EDI data
        2. **Eligibility Verification Check**: Confirm that insurance eligibility verification was performed
        3. **CPT Code Match Check**: Verify that CPT codes (e.g., 99214 for moderate-complexity visits) match the documentation complexity
        
        Analyze the provided data and return validation results.
        """
        
        try:
            if file_path:
                response = self.assistant.ask(question=validation_prompt, file_path=file_path)
            elif edi_837_content:
                response = self.assistant.ask(question=f"{validation_prompt}\n\nEDI 837 Content:\n{edi_837_content}")
            else:
                return {"error": "No file path or EDI content provided"}
            
            try:
                cleaned_response = self._extract_json_from_response(response)
                return json.loads(cleaned_response)
            except json.JSONDecodeError:
                return self._parse_text_response(response)
                
        except Exception as e:
            return {
                "error": f"Specific validation failed: {str(e)}",
                "validation_checks": {
                    "icd10_visible": False,
                    "eligibility_verified": False,
                    "cpt_matches_documentation": False
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
                "factor": "Missing ICD-10 on image documentation",
                "severity": "HIGH",
                "description": "ICD-10 codes must be visible on image-based bills for approval"
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
            recommendations.append("Include ICD-10 codes on image-based documentation")
        
        if "eligibility" in response.lower():
            recommendations.append("Perform insurance eligibility verification")
        
        if "cpt" in response.lower():
            recommendations.append("Verify CPT code matches documentation complexity")
        
        # Fallback recommendations
        if not recommendations:
            recommendations.append("Review claim documentation for completeness")
        
        # Validation checks
        validation_checks = {
            "icd10_visible": "icd" not in response.lower() or "missing" not in response.lower(),
            "eligibility_verified": "eligibility" not in response.lower() or "verified" in response.lower(),
            "cpt_matches_documentation": "cpt" not in response.lower() or "mismatch" not in response.lower()
        }
        
        return {
            "approval_prediction": {
                "likelihood": likelihood_match.group(1) if likelihood_match else "MEDIUM",
                "confidence_score": float(confidence_match.group(1)) if confidence_match else 0.5,
                "predicted_outcome": outcome_match.group(1) if outcome_match else "PENDING"
            },
            "risk_factors": risk_factors,
            "recommendations": recommendations,
            "validation_checks": validation_checks,
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
            
            # Add validation checks section
            validation_checks = result.get('validation_checks', {})
            if validation_checks:
                output += "\n### Validation Checks\n"
                for check, status in validation_checks.items():
                    status_icon = "✅" if status else "❌"
                    check_name = check.replace('_', ' ').title()
                    output += f"- {status_icon} {check_name}: {'Pass' if status else 'Fail'}\n"
            
            # Add consistency check section
            consistency_check = result.get('consistency_check', {})
            if consistency_check:
                output += "\n### EDI-Image Consistency Check\n"
                alignment_score = consistency_check.get('alignment_score', 0.0)
                overall_status = consistency_check.get('overall_status', 'UNKNOWN')
                
                # Status icon based on overall status
                if overall_status == "PASS":
                    status_icon = "✅"
                elif overall_status == "WARNING":
                    status_icon = "⚠️"
                elif overall_status == "FAIL":
                    status_icon = "❌"
                else:
                    status_icon = "❓"
                
                output += f"- {status_icon} **Overall Status**: {overall_status}\n"
                output += f"- **Alignment Score**: {alignment_score:.2f}/1.00\n"
                
                consistency_issues = consistency_check.get('consistency_issues', [])
                if consistency_issues:
                    output += "\n**Consistency Issues Found:**\n"
                    for issue in consistency_issues:
                        output += f"  • {issue}\n"
                else:
                    output += "\n**No consistency issues detected** ✅\n"
            
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
            description="Upload a medical document to predict claim approval likelihood using EDI 837 analysis."
        )
        
        iface.launch()

    def run_cli(self):
        """Run CLI-based interface for claim verification."""
        print("Medical Claim Verifier initialized.")
        print("Type 'exit' or 'quit' to end the conversation.")
        print("Commands:")
        print("- 'verify <file_path>': Verify a claim from document")
        print("- 'edi <edi_837_content>': Verify existing EDI 837 claim")
        print("- 'validate <file_path>': Validate specific requirements (ICD-10, eligibility, CPT)")

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

            elif user_input.startswith("edi "):
                edi_content = user_input[4:].strip()
                insurance = input("Insurance Provider (optional): ").strip() or None
                print("\nVerifying EDI 837 claim... Please wait.")
                result = self.verify_edi_837_claim(edi_content, insurance)
                print("\nClaim Verification Results:")
                print(json.dumps(result, indent=2))

            elif user_input.startswith("validate "):
                file_path = user_input[9:].strip()
                if not os.path.exists(file_path):
                    print(f"Error: File not found at path: {file_path}")
                    continue
                
                print("\nValidating specific requirements... Please wait.")
                result = self.validate_specific_requirements(file_path=file_path)
                print("\nSpecific Validation Results:")
                print(json.dumps(result, indent=2))

            else:
                print("Unknown command. Use 'verify', 'edi', or 'validate'.")
