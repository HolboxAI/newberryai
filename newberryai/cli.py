import argparse
import sys
from newberryai import ComplianceChecker
from newberryai import HealthScribe


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
    
    # Parse arguments and call the appropriate function
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()