import argparse
import sys
import os 
import pandas as pd
from newberryai import (ComplianceChecker, HealthScribe, DDxChat, Bill_extractor, ExcelExp, CodeReviewAssistant, RealtimeApp, PII_Redaction, PII_extraction, DocSummarizer, EDA, VideoGenerator, ImageGenerator, FaceRecognition, NL2SQL, PDFExtractor, FaceDetection,Handwrite2Text, ImageSearch, EDIGenerator, MedicalClaimVerifier, FeatureGptSummarizer, FeatureGptChat, FeatureGptImage, FeatureGptAgent)
import asyncio
from pathlib import Path
import json
import base64
from newberryai.virtual_tryon import VirtualTryOn
from newberryai.agent import Agent

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

def video_generator_command(args):
    """Handle the video generator subcommand."""
    generator = VideoGenerator()
    
    if args.gradio:
        print("Launching Gradio interface for Video Generator")
        generator.start_gradio()
    elif args.interactive:
        print("Starting interactive session for Video Generator")
        generator.run_cli()
    elif args.text:
        try:
            # Create request with provided parameters
            request = generator.VideoRequest(
                text=args.text,
                duration_seconds=args.duration,
                fps=args.fps,
                dimension=args.dimension,
                seed=args.seed
            )
            
            # Generate video
            print("Starting video generation...")
            loop = asyncio.get_event_loop()
            response = loop.run_until_complete(generator.generate(request))
            
            print("Waiting for video generation to complete...")
            final_response = loop.run_until_complete(generator.wait_for_completion(response.job_id))
            
            if final_response.status == "COMPLETED":
                print(f"Video generated successfully!")
                print(f"Video URL: {final_response.video_url}")
                
                # Download video if output path is specified
                if args.output:
                    output_path = Path(args.output)
                    if not output_path.parent.exists():
                        output_path.parent.mkdir(parents=True)
                    
                    # Download the video using the presigned URL
                    import requests
                    response = requests.get(final_response.video_url)
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    print(f"Video saved to: {output_path}")
            else:
                print(f"Video generation failed: {final_response.message}")
                
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Check the argument via --help")

def image_generator_command(args):
    """Handle the image generator subcommand."""
    generator = ImageGenerator()
    
    if args.gradio:
        print("Launching Gradio interface for Image Generator")
        generator.start_gradio()
    elif args.interactive:
        print("Starting interactive session for Image Generator")
        generator.run_cli()
    elif args.text:
        try:
            # Create request with provided parameters
            request = generator.ImageRequest(
                text=args.text,
                width=args.width,
                height=args.height,
                number_of_images=args.number_of_images,
                cfg_scale=args.cfg_scale,
                seed=args.seed,
                quality=args.quality
            )
            
            # Generate images
            print("Generating images...")
            loop = asyncio.get_event_loop()
            response = loop.run_until_complete(generator.generate(request))
            
            print(f"\nImages generated successfully!")
            print(f"Images saved in: {response.local_path}")
            print("\nImage URLs:")
            for url in response.images:
                print(url)
                
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Check the argument via --help")

def face_recognition_command(args):
    """Handle the face recognition subcommand."""
    face_recognition = FaceRecognition()
    
    if args.gradio:
        print("Launching Gradio interface for Face Recognition")
        face_recognition.start_gradio()
    elif args.interactive:
        print("Starting interactive session for Face Recognition")
        face_recognition.run_cli()
    elif args.image_path:
        try:
            if args.add:
                if not args.name:
                    print("Error: Name is required when adding a face")
                    sys.exit(1)
                response = face_recognition.add_to_collect(args.image_path, args.name)
            else:
                response = face_recognition.recognize_image(args.image_path)
            
            print("\nResult:")
            print(response["message"])
            if response["success"]:
                if response.get("name"):
                    print(f"Name: {response['name']}")
                if response.get("confidence"):
                    print(f"Confidence: {response['confidence']:.2f}%")
                if response.get("face_id"):
                    print(f"Face ID: {response['face_id']}")
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Check the argument via --help")

def nl2sql_command(args):
    """Handle the NL2SQL subcommand."""
    nl2sql = NL2SQL()
    
    if args.gradio:
        print("Launching Gradio interface for NL2SQL")
        nl2sql.start_gradio()
    elif args.interactive:
        print("Starting interactive session for NL2SQL")
        nl2sql.run_cli()
    elif args.question:
        # Check if database credentials are provided
        if not all([args.user, args.password, args.database]):
            print("Error: Database credentials (--user, --password, --database) are required when using --question")
            sys.exit(1)
            
        try:
            # Connect to database
            nl2sql.connect_to_database(
                host=args.host,
                user=args.user,
                password=args.password,
                database=args.database,
                port=args.port
            )
            
            # Process query
            response = nl2sql.process_query(args.question)
            
            print("\nResults:")
            if response["success"]:
                print(f"Generated SQL: {response['sql_query']}")
                print(f"Data: {json.dumps(response['data'], indent=2)}")
                print(f"Summary: {response['summary']}")
            else:
                print(f"Error: {response['message']}")
            
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Check the argument via --help")

def pdf_extraction_command(args):
    """Handle the PDF extraction subcommand."""
    extractor = PDFExtractor()
    
    if args.gradio:
        print("Launching Gradio interface for PDF Extraction")
        extractor.start_gradio()
    elif args.interactive:
        print("Starting interactive session for PDF Extraction")
        extractor.run_cli()
    elif args.file_path:
        # Validate that the file exists
        if not os.path.exists(args.file_path):
            print(f"Error: PDF file not found at path: {args.file_path}")
            sys.exit(1)
        
        print(f"Processing PDF: {args.file_path}")
        loop = asyncio.get_event_loop()
        pdf_id = loop.run_until_complete(extractor.process_pdf(args.file_path))
        
        if args.question:
            response = loop.run_until_complete(extractor.ask_question(pdf_id, args.question))
            print("\nAnswer:")
            print(response["answer"])
            print("\nSource Chunks:")
            for chunk in response["source_chunks"]:
                print(f"\n---\n{chunk}")
    else:
        print("Check the argument via --help")

def face_detection_command(args):
    """Handle the face detection subcommand."""
    face_detector = FaceDetection()
    
    if args.gradio:
        print("Launching Gradio interface for Face Detection")
        face_detector.start_gradio()
    elif args.interactive:
        print("Starting interactive session for Face Detection")
        face_detector.run_cli()
    elif args.add_image and args.name:
        try:
            # Add face to collection
            print(f"Adding face to collection: {args.name}")
            response = face_detector.add_face_to_collection(args.add_image, args.name)
            
            print("\nResult:")
            print(response["message"])
            if response["success"]:
                print(f"Face ID: {response['face_id']}")
                    
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)
    elif args.video_path:
        try:
            # Process video
            print("Processing video...")
            results = face_detector.process_video(args.video_path, args.max_frames)
            
            print("\nDetection Results:")
            for detection in results:
                print(f"\nTimestamp: {detection['timestamp']}s")
                if detection.get('external_image_id'):
                    print(f"Matched Face: {detection['external_image_id']}")
                    print(f"Face ID: {detection['face_id']}")
                    print(f"Confidence: {detection['confidence']:.2f}%")
                else:
                    print("No match found in collection")
                    
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Check the argument via --help")

def virtual_tryon_command(args):
    """Handle the virtual try-on subcommand."""
    try_on = VirtualTryOn()
    
    if args.gradio:
        print("Launching Gradio interface for Virtual Try-On")
        try_on.start_gradio()
    elif args.interactive:
        print("Starting interactive session for Virtual Try-On")
        try_on.run_cli()
    elif args.model_image and args.garment_image:
        try:
            # Convert images to base64
            model_b64 = base64.b64encode(open(args.model_image, "rb").read()).decode()
            garment_b64 = base64.b64encode(open(args.garment_image, "rb").read()).decode()
            
            # Create request
            request = try_on.TryOnRequest(
                model_image=model_b64,
                garment_image=garment_b64,
                category=args.category
            )
            
            # Process request
            print("Processing virtual try-on...")
            loop = asyncio.get_event_loop()
            response = loop.run_until_complete(try_on.process(request))
            
            # Wait for completion
            while True:
                status = loop.run_until_complete(try_on.get_status(response.job_id))
                if status.status in ["completed", "failed"]:
                    break
                asyncio.sleep(3)
            
            if status.status == "completed" and status.output:
                print("\nVirtual try-on completed successfully!")
                print("\nGenerated images:")
                for url in status.output:
                    print(url)
            else:
                print("\nVirtual try-on failed!")
                
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Check the argument via --help")

def agent_command(args):
    """Handle agent-related commands"""
    agent = Agent()
    
    if args.gradio:
        print("Launching Gradio interface for Agent")
        agent.start_gradio()
    elif args.interactive:
        print("Starting interactive session for Agent")
        agent.run_cli()
    elif args.query:
        print(f"Query: {args.query}\n")
        response = agent.process_query(args.query)
        print("Response:")
        print(response)
    else:
        print("Check the argument via --help")

def handwrite2text_command(args):
    handwriter = Handwrite2Text()
    if args.gradio:
        print("Launching Gradio interface for Handwriting to Text Converter")
        handwriter.start_gradio()
    elif args.interactive:
        print("Starting interactive session for Handwriting to Text Converter")
        handwriter.run_cli()
    elif args.file_path:
        if not os.path.exists(args.file_path):
            print(f"Error: Image file not found at path: {args.file_path}")
            sys.exit(1)
        print(f"Extracting text from: {args.file_path}")
        response = handwriter.extract_text(args.file_path)
        print("\nExtracted Text:")
        print(response)
    else:
        print("Check the argument via --help")

def img_search_command(args):
    searcher = ImageSearch(s3_bucket=args.s3_bucket)
    if args.build_index:
        searcher.build_index(prefix=args.prefix)
    elif args.gradio:
        searcher.start_gradio()
    elif args.cli:
        searcher.run_cli()
    else:
        print("No action specified. Use --build_index, --gradio, or --cli.")

def edi835_command(args):
    extractor = EDIGenerator(edi_type="835")
    if args.gradio:
        print(f"Launching Gradio interface for EDI 835 Generator")
        extractor.start_gradio()
    elif args.interactive:
        extractor.run_cli()
    elif args.file_path:
        if not os.path.exists(args.file_path):
            print(f"Error: Document file not found at path: {args.file_path}")
            sys.exit(1)
        print(f"Generating EDI 835 for document: {args.file_path}")
        response = extractor.analyze_document(args.file_path)
        print("\nEDI 835 Output:")
        print(response)
    else:
        print("Check the argument via --help")

def edi837_command(args):
    extractor = EDIGenerator(edi_type="837")
    if args.gradio:
        print(f"Launching Gradio interface for EDI 837 Generator")
        extractor.start_gradio()
    elif args.interactive:
        extractor.run_cli()
    elif args.file_path:
        if not os.path.exists(args.file_path):
            print(f"Error: Document file not found at path: {args.file_path}")
            sys.exit(1)
        print(f"Generating EDI 837 for document: {args.file_path}")
        response = extractor.analyze_document(args.file_path)
        print("\nEDI 837 Output:")
        print(response)
    else:
        print("Check the argument via --help")

def edi270_command(args):
    extractor = EDIGenerator(edi_type="270")
    if args.gradio:
        print(f"Launching Gradio interface for EDI 270 Generator")
        extractor.start_gradio()
    elif args.interactive:
        extractor.run_cli()
    elif args.file_path:
        if not os.path.exists(args.file_path):
            print(f"Error: Document file not found at path: {args.file_path}")
            sys.exit(1)
        print(f"Generating EDI 270 for document: {args.file_path}")
        response = extractor.analyze_document(args.file_path)
        print("\nEDI 270 Output:")
        print(response)
    else:
        print("Check the argument via --help")

def claim_verifier_command(args):
    """Handle the medical claim verifier subcommand."""
    verifier = MedicalClaimVerifier()
    
    if args.gradio:
        print("Launching Gradio interface for Medical Claim Verifier")
        verifier.start_gradio()
    elif args.interactive:
        verifier.run_cli()
    elif args.file_path:
        if not os.path.exists(args.file_path):
            print(f"Error: Document file not found at path: {args.file_path}")
            sys.exit(1)
        print(f"Verifying claim from document: {args.file_path}")
        result = verifier.verify_claim_from_document(args.file_path, args.insurance_provider)
        print("\nClaim Verification Results:")
        print(json.dumps(result, indent=2))
    else:
        print("Check the argument via --help")

def feature_gpt_summarizer_command(args):
    """Handle the GPT-5 PDF summarizer subcommand."""
    summarizer = FeatureGptSummarizer()
    if args.gradio:
        print("Launching Gradio interface for GPT-5 PDF Summarizer")
        summarizer.start_gradio()
    elif args.interactive:
        print("Starting interactive session for GPT-5 PDF Summarizer")
        summarizer.run_cli()
    elif args.file_path:
        print(f"Analyzing document: {args.file_path}")
        response = summarizer.ask(args.file_path)
        print("\nSummary:")
        print(response)
    else:
        print("Check the argument via --help")

def feature_gpt_chat_command(args):
    """Handle the GPT-5 chat assistant subcommand."""
    chat = FeatureGptChat()
    if args.gradio:
        print("Launching Gradio interface for GPT-5 Chat Assistant")
        chat.start_gradio()
    elif args.interactive:
        print("Starting interactive session for GPT-5 Chat Assistant")
        chat.run_cli()
    elif args.message:
        print(f"Message: {args.message}")
        response = chat.ask(args.message)
        print("\nResponse:")
        print(response)
    else:
        print("Check the argument via --help")

def feature_gpt_image_command(args):
    """Handle the GPT-5 image analysis subcommand."""
    image = FeatureGptImage()
    if args.gradio:
        print("Launching Gradio interface for GPT-5 Image Analyzer")
        image.start_gradio()
    elif args.interactive:
        print("Starting interactive session for GPT-5 Image Analyzer")
        image.run_cli()
    elif args.file_path:
        print(f"Analyzing image: {args.file_path}")
        response = image.ask(args.file_path)
        print("\nImage Analysis:")
        print(response)
    else:
        print("Check the argument via --help")

def feature_gpt_agent_command(args):
    """Handle the GPT-5 agent subcommand."""
    agent = FeatureGptAgent()
    if args.gradio:
        print("Launching Gradio interface for GPT-5 Agent")
        agent.start_gradio()
    elif args.interactive:
        print("Starting interactive session for GPT-5 Agent")
        agent.run_cli()
    elif args.instruction:
        print(f"Instruction: {args.instruction}")
        response = agent.ask(args.instruction)
        print("\nAgent Response:")
        print(response)
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

    # Video Generator Command
    video_parser = subparsers.add_parser('video', help='Generate videos from text using AI')
    video_parser.add_argument("--text", "-t", type=str, help="Text prompt for video generation")
    video_parser.add_argument("--duration", "-d", type=int, default=6, help="Duration in seconds (1-30)")
    video_parser.add_argument("--fps", "-f", type=int, default=24, help="Frames per second (1-60)")
    video_parser.add_argument("--dimension", "-dim", default="1280x720", 
                          choices=["1280x720", "1920x1080", "3840x2160"],
                          help="Video dimensions")
    video_parser.add_argument("--seed", "-s", type=int, default=42, help="Random seed for generation")
    video_parser.add_argument("--output", "-o", help="Output file path for the video")
    video_parser.add_argument("--gradio", "-g", action="store_true", 
                        help="Launch Gradio interface")
    video_parser.add_argument("--interactive", "-i", action="store_true",
                        help="Run in interactive CLI mode")
    video_parser.set_defaults(func=video_generator_command)

    # Image Generator Command
    image_parser = subparsers.add_parser('image', help='Generate images from text using AI')
    image_parser.add_argument("--text", "-t", type=str, help="Text prompt for image generation")
    image_parser.add_argument("--width", "-w", type=int, default=1024, help="Width of the image (512-1024)")
    image_parser.add_argument("--height", "-ht", type=int, default=1024, help="Height of the image (512-1024)")
    image_parser.add_argument("--number_of_images", "-n", type=int, default=1, help="Number of images to generate (1-4)")
    image_parser.add_argument("--cfg_scale", "-c", type=int, default=8, help="CFG scale (1-20)")
    image_parser.add_argument("--seed", "-s", type=int, default=42, help="Random seed for generation")
    image_parser.add_argument("--quality", "-q", default="standard", 
                          choices=["standard", "premium"],
                          help="Quality of the generated image")
    image_parser.add_argument("--gradio", "-g", action="store_true", 
                        help="Launch Gradio interface")
    image_parser.add_argument("--interactive", "-i", action="store_true",
                        help="Run in interactive CLI mode")
    image_parser.set_defaults(func=image_generator_command)

    # Face Recognition Command
    face_parser = subparsers.add_parser('face_recognig', help='Face recognition using AWS Rekognition')
    face_parser.add_argument("--image_path", "-i", type=str, help="Path to the image file")
    face_parser.add_argument("--add", "-a", action="store_true", help="Add face to collection")
    face_parser.add_argument("--name", "-n", type=str, help="Name to associate with the face (required for add)")
    face_parser.add_argument("--gradio", "-g", action="store_true", 
                        help="Launch Gradio interface")
    face_parser.add_argument("--interactive", "-int", action="store_true",
                        help="Run in interactive CLI mode")
    face_parser.set_defaults(func=face_recognition_command)

    # NL2SQL Command
    nl2sql_parser = subparsers.add_parser('nl2sql', help='Convert natural language to SQL queries')
    nl2sql_parser.add_argument("--question", "-q", type=str, help="Natural language question to convert to SQL")
    nl2sql_parser.add_argument("--host", type=str, default="localhost", help="Database host")
    nl2sql_parser.add_argument("--user", type=str, help="Database username")
    nl2sql_parser.add_argument("--password", type=str, help="Database password")
    nl2sql_parser.add_argument("--database", type=str, help="Database name")
    nl2sql_parser.add_argument("--port", type=int, default=3306, help="Database port")
    nl2sql_parser.add_argument("--gradio", "-g", action="store_true", 
                        help="Launch Gradio interface")
    nl2sql_parser.add_argument("--interactive", "-i", action="store_true",
                        help="Run in interactive CLI mode")
    nl2sql_parser.set_defaults(func=nl2sql_command)

    # PDF Extraction Command
    pdf_extraction_parser = subparsers.add_parser('pdf_extract', help='Extract and query content from PDF documents')
    pdf_extraction_parser.add_argument("--file_path", "-f", type=str, help="Path to the PDF document to analyze")
    pdf_extraction_parser.add_argument("--question", "-q", type=str, help="Question to ask about the PDF content")
    pdf_extraction_parser.add_argument("--gradio", "-g", action="store_true", 
                        help="Launch Gradio interface")
    pdf_extraction_parser.add_argument("--interactive", "-i", action="store_true",
                        help="Run in interactive CLI mode")
    pdf_extraction_parser.set_defaults(func=pdf_extraction_command)

    # Face Detection Command
    face_detect_parser = subparsers.add_parser('face_detect', help='Process videos and detect faces using AWS Rekognition')
    face_detect_parser.add_argument("--video_path", "-v", type=str, help="Path to the video file")
    face_detect_parser.add_argument("--max_frames", "-m", type=int, default=20, help="Maximum number of frames to process")
    face_detect_parser.add_argument("--add_image", "-a", type=str, help="Path to the image to add to collection")
    face_detect_parser.add_argument("--name", "-n", type=str, help="Name to associate with the image")
    face_detect_parser.add_argument("--gradio", "-g", action="store_true", 
                        help="Launch Gradio interface")
    face_detect_parser.add_argument("--interactive", "-i", action="store_true",
                        help="Run in interactive CLI mode")
    face_detect_parser.set_defaults(func=face_detection_command)

    # Virtual Try-On Command
    tryon_parser = subparsers.add_parser('tryon', help='Generate virtual try-on images')
    tryon_parser.add_argument("--model_image", "-m", type=str, help="Path to model image")
    tryon_parser.add_argument("--garment_image", "-g", type=str, help="Path to garment image")
    tryon_parser.add_argument("--category", "-c", default="tops",
                          choices=["tops", "bottoms", "dresses", "outerwear"],
                          help="Category of the garment")
    tryon_parser.add_argument("--gradio", "-G", action="store_true", 
                        help="Launch Gradio interface")
    tryon_parser.add_argument("--interactive", "-i", action="store_true",
                        help="Run in interactive CLI mode")
    tryon_parser.set_defaults(func=virtual_tryon_command)

    # Add agent subparser
    agent_parser = subparsers.add_parser('agent', help='Run the agent')
    agent_parser.add_argument('--gradio', '-g', action='store_true', help='Launch Gradio interface')
    agent_parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode')
    agent_parser.add_argument('--query', '-q', type=str, help='Process a single query')
    # Handwrite2Text Command
    handwrite2text_parser = subparsers.add_parser('handwrite2text', help='Convert handwritten document images to digital text')
    handwrite2text_parser.add_argument('--file_path', '-f', type=str, help='Path to the handwritten image file')
    handwrite2text_parser.add_argument('--gradio', '-g', action='store_true', help='Launch Gradio interface')
    handwrite2text_parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive CLI mode')
    handwrite2text_parser.set_defaults(func=handwrite2text_command)

    # Titan Image Search Command
    img_search_parser = subparsers.add_parser('img_search', help='Semantic image search using S3, Amazon Titan and FAISS')
    img_search_parser.add_argument('--s3_bucket', required=True, help='S3 bucket name')
    img_search_parser.add_argument('--build_index', action='store_true', help='Build index from S3 images')
    img_search_parser.add_argument('--prefix', default='', help='S3 prefix/folder (optional)')
    img_search_parser.add_argument('--gradio', action='store_true', help='Launch Gradio UI')
    img_search_parser.add_argument('--cli', action='store_true', help='Run CLI')
    img_search_parser.set_defaults(func=img_search_command)

    # EDI 835 Command
    edi835_parser = subparsers.add_parser('edi835', help='Generate EDI 835 from medical documents')
    edi835_parser.add_argument("--file_path", "-fp", type=str, help="Path to a document to analyze")
    edi835_parser.add_argument("--gradio", "-g", action="store_true", help="Launch Gradio interface")
    edi835_parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive CLI mode")
    edi835_parser.set_defaults(func=edi835_command)

    # EDI 837 Command
    edi837_parser = subparsers.add_parser('edi837', help='Generate EDI 837 from medical documents')
    edi837_parser.add_argument("--file_path", "-fp", type=str, help="Path to a document to analyze")
    edi837_parser.add_argument("--gradio", "-g", action="store_true", help="Launch Gradio interface")
    edi837_parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive CLI mode")
    edi837_parser.set_defaults(func=edi837_command)

    # EDI 270 Command
    edi270_parser = subparsers.add_parser('edi270', help='Generate EDI 270 from medical documents')
    edi270_parser.add_argument("--file_path", "-fp", type=str, help="Path to a document to analyze")
    edi270_parser.add_argument("--gradio", "-g", action="store_true", help="Launch Gradio interface")
    edi270_parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive CLI mode")
    edi270_parser.set_defaults(func=edi270_command)

    # Medical Claim Verifier Command
    claim_verifier_parser = subparsers.add_parser('claim_verifier', help='Verify medical claims and predict approval likelihood')
    claim_verifier_parser.add_argument("--file_path", "-fp", type=str, help="Path to a medical document to verify")
    claim_verifier_parser.add_argument("--insurance_provider", "-ip", type=str, help="Insurance provider name for specific analysis")
    claim_verifier_parser.add_argument("--gradio", "-g", action="store_true", help="Launch Gradio interface")
    claim_verifier_parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive CLI mode")
    claim_verifier_parser.set_defaults(func=claim_verifier_command)

    # Feature GPT-5 Summarizer Command
    feature_gpt5_summarizer_parser = subparsers.add_parser('feature_gpt5_summarizer', help='Extract and summarize content from PDF documents using GPT-5')
    feature_gpt5_summarizer_parser.add_argument("--file_path", "-f", type=str, help="Path to the PDF document to analyze")
    feature_gpt5_summarizer_parser.add_argument("--gradio", "-g", action="store_true", help="Launch Gradio interface")
    feature_gpt5_summarizer_parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive CLI mode")
    feature_gpt5_summarizer_parser.set_defaults(func=feature_gpt_summarizer_command)

    # Feature GPT-5 Chat Assistant Command
    feature_gpt5_chat_parser = subparsers.add_parser('feature_gpt5_chat', help='Chat with GPT-5 AI assistant')
    feature_gpt5_chat_parser.add_argument("--message", "-m", type=str, help="Message to send to the chat assistant")
    feature_gpt5_chat_parser.add_argument("--gradio", "-g", action="store_true", help="Launch Gradio interface")
    feature_gpt5_chat_parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive CLI mode")
    feature_gpt5_chat_parser.set_defaults(func=feature_gpt_chat_command)

    # Feature GPT-5 Image Analyzer Command
    feature_gpt5_image_parser = subparsers.add_parser('feature_gpt5_image', help='Analyze images using GPT-5')
    feature_gpt5_image_parser.add_argument("--file_path", "-f", type=str, help="Path to the image file to analyze")
    feature_gpt5_image_parser.add_argument("--gradio", "-g", action="store_true", help="Launch Gradio interface")
    feature_gpt5_image_parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive CLI mode")
    feature_gpt5_image_parser.set_defaults(func=feature_gpt_image_command)

    # Feature GPT-5 Agent Command (already implemented handler: feature_gpt5_agent_command)
    feature_gpt5_agent_parser = subparsers.add_parser('feature_gpt5_agent', help='Use GPT-5 as an advanced agent for reasoning and tasks')
    feature_gpt5_agent_parser.add_argument("--instruction", "-i", type=str, help="Instruction or question for the agent")
    feature_gpt5_agent_parser.add_argument("--gradio", "-g", action="store_true", help="Launch Gradio interface")
    feature_gpt5_agent_parser.add_argument("--interactive", "-I", action="store_true", help="Run in interactive CLI mode")
    feature_gpt5_agent_parser.set_defaults(func=feature_gpt_agent_command)

    # Parse arguments and call the appropriate function
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
