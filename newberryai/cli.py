import argparse
import sys
from newberryai import ComplianceChecker
from newberryai import HealthScribe
from newberryai import DDxChat
from newberryai import Bill_extractor
import os 

def compliance_command(args):
    """Handle the compliance subcommand."""
    checker = ComplianceChecker()
    
    result, status_code = checker.check_compliance(args.video_file, args.question)
    
    if status_code:
        print(f"Error: {result.get('error', 'Unknown error')}")
        sys.exit(1)
    
    print("\n=== Compliance Analysis ===")
    print(f"Compliant: {'Yes' if result['compliant'] else 'No'}")
    print("\n=== Analysis Details ===")
    print(result["analysis"])


def healthscribe_command(args):
    """Handle the healthscribe subcommand."""
    healthscribe = HealthScribe(
        data_access_role_arn=args.data_access_role_arn,
        input_s3_bucket=args.input_s3_bucket,
        
    )
    
    summary = healthscribe.process(
        file_path=args.file_path,
        job_name=args.job_name,
        output_s3_bucket=args.output_s3_bucket,
        s3_key=args.s3_key
    )
    
    print("\n=== Medical Transcription Summary ===")
    print(summary.summary)


def differential_diagnosis_command(args):
    ddx_chat = DDxChat()
    
    if args.gradio:
        print("Launching Gradio interface for DDx Assistant")
        ddx_chat.start_gradio()
    elif args.interactive:
        print("Starting interactive session for DDx Assistant")
        ddx_chat.run_cli()
    elif args.clinical_indication:
        print(f"Question: {args.clinical_indication}\n")
        response = ddx_chat.ask(args.clinical_indication)
        print("Response:")
        print(response)
    else: 
        print("Check the argument via --help")



def medical_bill_extractor_command(args):
    extract_bill = Bill_extractor()
    if args.gradio:
        print(f"Launching Gradio interface for Document Analysis")
        extract_bill.start_gradio()

    elif args.interactive:
        extract_bill.run_cli()

    elif args.image_path:
        # Validate that the image file exists
        if not os.path.exists(args.image_path):
            print(f"Error: Document file not found at path: {args.image_path}")
            sys.exit(1)
        
        print(f"Analyzing document: {args.image_path}")
        response = extract_bill.analyze_document(args.image_path)
        
        print("\nAnalysis:")
        print(response)
    else:
        print("Check the argument via --help")


def main():
    """Command line interface for NewberryAI tools."""
    parser = argparse.ArgumentParser(description='NewberryAI - AWS Powered tools for medical domain')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    subparsers.required = True
    
    # Compliance Check Command
    compliance_parser = subparsers.add_parser('compliance', help='Run compliance check on video')
    compliance_parser.add_argument('--video_file', required=True, help='Path to the video file')
    compliance_parser.add_argument('--question', required=True, help='Compliance question to check')
    compliance_parser.set_defaults(func=compliance_command)
    
    # Healthscribe Command
    healthscribe_parser = subparsers.add_parser('healthscribe', help='Run medical transcription using AWS HealthScribe')
    healthscribe_parser.add_argument('--file_path', required=True, help='Path to the audio file')
    healthscribe_parser.add_argument('--job_name', required=True, help='Transcription job name')
    healthscribe_parser.add_argument('--data_access_role_arn', required=True, 
                                     help='ARN of role with S3 bucket permissions')
    healthscribe_parser.add_argument('--input_s3_bucket', required=True, help='Input S3 bucket name')
    healthscribe_parser.add_argument('--output_s3_bucket', required=True, help='Output S3 bucket name')
    healthscribe_parser.add_argument('--s3_key', default=None, 
                                     help='S3 key for the uploaded audio file (Optional)')
    healthscribe_parser.set_defaults(func=healthscribe_command)
    

    # Differential Diagonosis Command 
    differential_diagnosis_parser = subparsers.add_parser('ddx', help='Run differential Diagnosis on medical data')
    differential_diagnosis_parser.add_argument("--clinical_indication", "-ci", type=str, help="Clinical question for the DDx Assistant")
    differential_diagnosis_parser.add_argument("--gradio", "-g", action="store_true", 
                        help="Launch Gradio interface")
    differential_diagnosis_parser.add_argument("--interactive", "-i", action="store_true",
                        help="Run in interactive CLI mode")
    differential_diagnosis_parser.set_defaults(func=differential_diagnosis_command)

    # Medical Bill Extractor Command 
    medical_bill_extractor_parser = subparsers.add_parser('bill_extract', help='Extract metadata from medical bills')
    medical_bill_extractor_parser.add_argument("--image_path", "-img", type=str, help="Path to a document image to analyze")
    medical_bill_extractor_parser.add_argument("--gradio", "-g", action="store_true", 
                        help="Launch Gradio interface")
    medical_bill_extractor_parser.add_argument("--interactive", "-i", action="store_true",
                        help="Run in interactive CLI mode")
    medical_bill_extractor_parser.set_defaults(func=medical_bill_extractor_command)

    # Parse arguments and call the appropriate function
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()