import argparse
import sys
import os 
import pandas as pd
from newberryai import (ComplianceChecker, HealthScribe, DDxChat, Bill_extractor, ExcelExp, CodeReviewAssistant, RealtimeApp, PII_Redaction, PII_extraction, DocSummarizer, EDA)

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

def excel_formula_command(args):
    Excelo_chat = ExcelExp()
    
    if args.gradio:
        print("Launching Gradio interface for AI Assistant")
        Excelo_chat.start_gradio()
    elif args.interactive:
        print("Starting interactive session for AI Assistant")
        Excelo_chat.run_cli()
    elif args.Excel_query:
        print(f"Question: {args.Excel_query}\n")
        response = Excelo_chat.ask(args.Excel_query)
        print("Response:")
        print(response)
    else: 
        print("Check the argument via --help")

def code_debugger_command(args):
    debugger = CodeReviewAssistant()
    
    if args.gradio:
        print("Launching Gradio interface for AI Assistant")
        debugger.start_gradio()
    elif args.interactive:
        print("Starting interactive session for AI Assistant")
        debugger.run_cli()
    elif args.code_query:
        print(f"Question: {args.code_query}\n")
        response = debugger.ask(args.code_query)
        print("Response:")
        print(response)
    else: 
        print("Check the argument via --help")

def pii_redactor_command(args):
    pii_red = PII_Redaction()
    
    if args.gradio:
        print("Launching Gradio interface for AI Assistant")
        pii_red.start_gradio()
    elif args.interactive:
        print("Starting interactive session for AI Assistant")
        pii_red.run_cli()
    elif args.text:
        print(f"Question: {args.text}\n")
        response = pii_red.ask(args.text)
        print("Response:")
        print(response)
    else: 
        print("Check the argument via --help")

def pii_extractor_command(args):
    pii_red = PII_extraction()
    
    if args.gradio:
        print("Launching Gradio interface for AI Assistant")
        pii_red.start_gradio()
    elif args.interactive:
        print("Starting interactive session for AI Assistant")
        pii_red.run_cli()
    elif args.text:
        print(f"Question: {args.text}\n")
        response = pii_red.ask(args.text)
        print("Response:")
        print(response)
    else: 
        print("Check the argument via --help")

def speech_to_speech_command(args):
    """Handle the speech-to-speech subcommand."""
    print("Launching Speech-to-Speech Assistant...")
    app = RealtimeApp()
    app.run()


def medical_bill_extractor_command(args):
    extract_bill = Bill_extractor()
    if args.gradio:
        print(f"Launching Gradio interface for Document Analysis")
        extract_bill.start_gradio()

    elif args.interactive:
        extract_bill.run_cli()

    elif args.file_path:
        # Validate that the file exists
        if not os.path.exists(args.file_path):
            print(f"Error: Document file not found at path: {args.file_path}")
            sys.exit(1)
        
        print(f"Analyzing document: {args.file_path}")
        response = extract_bill.analyze_document(args.file_path)
        
        print("\nAnalysis:")
        print(response)
    else:
        print("Check the argument via --help")

def pdf_summarizer_command(args):
    """Handle the PDF summarizer subcommand."""
    summarizer = DocSummarizer()
    
    if args.gradio:
        print("Launching Gradio interface for PDF Summarizer")
        summarizer.start_gradio()
    elif args.interactive:
        print("Starting interactive session for PDF Summarizer")
        summarizer.run_cli()
    elif args.file_path:
        # Validate that the document file exists
        if not os.path.exists(args.file_path):
            print(f"Error: Document file not found at path: {args.file_path}")
            sys.exit(1)
        
        print(f"Analyzing document: {args.file_path}")
        response = summarizer.ask(args.file_path)
        
        print("\nSummary:")
        print(response)
    else:
        print("Check the argument via --help")

def eda_command(args):
    """Handle the EDA subcommand."""
    eda = EDA()
    
    if args.gradio:
        print("Launching Gradio interface for EDA Assistant")
        eda.start_gradio()
    elif args.interactive:
        print("Starting interactive session for EDA Assistant")
        eda.run_cli()
    elif args.file_path:
        # Validate that the file exists
        if not os.path.exists(args.file_path):
            print(f"Error: File not found at path: {args.file_path}")
            sys.exit(1)
        
        print(f"Loaded dataset: {args.file_path}")
        eda.current_data = pd.read_csv(args.file_path)
        print("You can now ask questions about the data using the interactive CLI (use --interactive) or Gradio (use --gradio).")
        if args.visualize:
            print("\nGenerating visualizations...")
            eda.visualize_data()
    else:
        print("Check the argument via --help")

def main():
    """Command line interface for NewberryAI tools."""
    parser = argparse.ArgumentParser(description='NewberryAI - AI Powered tools using LLMs ')
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

    # Excel Formula Generator Command 
    Excelo_parser = subparsers.add_parser('ExcelO', help='Ask Excel Formula for your spreadsheet')
    Excelo_parser.add_argument("--Excel_query", "-Eq", type=str, help="Your Excel Query for AI Assistant")
    Excelo_parser.add_argument("--gradio", "-g", action="store_true", 
                        help="Launch Gradio interface")
    Excelo_parser.add_argument("--interactive", "-i", action="store_true",
                        help="Run in interactive CLI mode")
    Excelo_parser.set_defaults(func=excel_formula_command)

    # Code Assistant and Debugger
    coder_parser = subparsers.add_parser('Coder', help='Ask for help in python coding')
    coder_parser.add_argument("--code_query", "-cq", type=str, help="Your Code Query for AI Assistant")
    coder_parser.add_argument("--gradio", "-g", action="store_true", 
                        help="Launch Gradio interface")
    coder_parser.add_argument("--interactive", "-i", action="store_true",
                        help="Run in interactive CLI mode")
    coder_parser.set_defaults(func=code_debugger_command)

    # PII Redactor AI Assistant
    pii_parser = subparsers.add_parser('PII_Red', help='Ask for help in redaction of PII from text')
    pii_parser.add_argument("--text", "-t", type=str, help="Your text for AI Assistant")
    pii_parser.add_argument("--gradio", "-g", action="store_true", 
                        help="Launch Gradio interface")
    pii_parser.add_argument("--interactive", "-i", action="store_true",
                        help="Run in interactive CLI mode")
    pii_parser.set_defaults(func=pii_redactor_command)

    # PII Extractor AI Assistant
    pii_ex_parser = subparsers.add_parser('PII_extract', help='Ask for help in extraction of PII from text')
    pii_ex_parser.add_argument("--text", "-t", type=str, help="Your text for AI Assistant")
    pii_ex_parser.add_argument("--gradio", "-g", action="store_true", 
                        help="Launch Gradio interface")
    pii_ex_parser.add_argument("--interactive", "-i", action="store_true",
                        help="Run in interactive CLI mode")
    pii_ex_parser.set_defaults(func=pii_extractor_command)


    # Medical Bill Extractor Command 
    medical_bill_extractor_parser = subparsers.add_parser('bill_extract', help='Extract metadata from medical bills')
    medical_bill_extractor_parser.add_argument("--file_path", "-fp", type=str, help="Path to a document to analyze")
    medical_bill_extractor_parser.add_argument("--gradio", "-g", action="store_true", 
                        help="Launch Gradio interface")
    medical_bill_extractor_parser.add_argument("--interactive", "-i", action="store_true",
                        help="Run in interactive CLI mode")
    medical_bill_extractor_parser.set_defaults(func=medical_bill_extractor_command)
    
    # Speech to speech
    speech_to_speech_parser = subparsers.add_parser('speech_to_speech', help='Launch real-time Speech-to-Speech AI Assistant')
    speech_to_speech_parser.set_defaults(func=speech_to_speech_command)

    # PDF Summarizer Command
    pdf_summarizer_parser = subparsers.add_parser('pdf_summarizer', help='Extract and summarize content from PDF documents')
    pdf_summarizer_parser.add_argument("--file_path", "-d", type=str, help="Path to the PDF document to analyze")
    pdf_summarizer_parser.add_argument("--gradio", "-g", action="store_true", 
                        help="Launch Gradio interface")
    pdf_summarizer_parser.add_argument("--interactive", "-i", action="store_true",
                        help="Run in interactive CLI mode")
    pdf_summarizer_parser.set_defaults(func=pdf_summarizer_command)

    # EDA Command
    eda_parser = subparsers.add_parser('eda', help='Perform Exploratory Data Analysis on datasets')
    eda_parser.add_argument("--file_path", "-f", type=str, help="Path to the CSV file to analyze")
    eda_parser.add_argument("--gradio", "-g", action="store_true", 
                        help="Launch Gradio interface")
    eda_parser.add_argument("--interactive", "-i", action="store_true",
                        help="Run in interactive CLI mode")
    eda_parser.add_argument("--visualize", "-v", action="store_true",
                        help="Generate visualizations for the dataset")
    eda_parser.set_defaults(func=eda_command)

    # Parse arguments and call the appropriate function
    args = parser.parse_args()
    args.func(args)
if __name__ == '__main__':
    main()
