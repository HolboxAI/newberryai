import argparse
from newberryai import healthscribe


def main():
    parser = argparse.ArgumentParser(description='Medical Scribing using AWS HealthScribe Service')
    parser.add_argument('audio_file', help='Path to the audio file')
    parser.add_argument('job_name', help='Transcription job name')
    parser.add_argument('data_access_role_arn',help='ARN of role which has the minimum permission of s3 bucket for input and output')
    parser.add_argument('s3_bucket', help='Target S3 bucket name')
    parser.add_argument('--s3_key', help='S3 key for the uploaded audio file', default=None)
    args = parser.parse_args()
    result = healthscribe(args.audio_file,args.job_name,args.data_access_role_arn, args.s3_bucket, args.s3_key)
    print(result)


if __name__ == '__main__':
    main()
