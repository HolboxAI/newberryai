# NewberryAI

A Python package for medical scribing using AWS Transcribe Medical service.

## Overview

HealthScribe is a package focused on the healthcare domain. It enables medical scribing by transcribing audio files (e.g., doctor-patient conversations) using AWS Transcribe Medical service. The package uploads the provided audio file to an S3 bucket, starts a transcription job, and retrieves a summary from the job's JSON output.

## Installation

```sh
 pip install newberryai
```
## Usage

You can use the command-line interface:

```bash
healthscribe-cli <audio_file> <job_name> <data_access_role_arn> <s3_bucket> 
```

For example:

```bash
healthscribe-cli conversation.wav myJob arn:aws:iam::aws_accountid:role/your-role my-s3-bucket s3-key
```

You can use this in python script: 
```sh 
import os
import newberryai

# Set the environment variables for the AWS SDK
os.environ['AWS_ACCESS_KEY_ID'] = aws_access_key_id
os.environ['AWS_SECRET_ACCESS_KEY'] = aws_secret_access_key
os.environ['AWS_REGION'] = aws_region

# Call the function with sensitive information masked
summary = newberryai.healthscribe(
    audio_file="/path/to/audio.mp3",
    job_name="job_name",
    data_access_role_arn="arn:aws:iam::accountid:role/your-role",
    s3_bucket="s3_bucket"
)

print(summary)
```


## License

This project is licensed under the MIT License.
