import argparse
from newberryai import healthscribe, check_compliance


def main():
    parser = argparse.ArgumentParser(description='Medical Scribing using AWS HealthScribe Service or Video Compliance Check')
    subparsers = parser.add_subparsers(help='commands')

    # Healthscribe Command
    healthscribe_parser = subparsers.add_parser('healthscribe', help='Run Healthscribe transcription')
    healthscribe_parser.add_argument('audio_file', help='Path to the audio file')
    healthscribe_parser.add_argument('job_name', help='Transcription job name')
    healthscribe_parser.add_argument('data_access_role_arn', help='ARN of role which has the minimum permission of s3 bucket for input and output')
    healthscribe_parser.add_argument('s3_bucket', help='Target S3 bucket name')
    healthscribe_parser.add_argument('--s3_key', help='S3 key for the uploaded audio file', default=None)
    
    # Compliance Check Command
    compliance_parser = subparsers.add_parser('compliance', help='Run Compliance Check on Video')
    compliance_parser.add_argument('video_file', help='Path to the video file')
    compliance_parser.add_argument('question', help='Compliance question to check')
    
    args = parser.parse_args()

    if hasattr(args, 'audio_file'):  # If we are using Healthscribe
        result = healthscribe(args.audio_file, args.job_name, args.data_access_role_arn, args.s3_bucket, args.s3_key)
        print(result)
    elif hasattr(args, 'video_file'):  # If we are using Compliance check
        result = check_compliance(args.video_file, args.question)
        print(result)


if __name__ == '__main__':
    main()
