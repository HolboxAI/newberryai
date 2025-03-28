# NewberryAI

A Python package for AI tools using AWS service.

## Overview

- **Compliance Checker**: Analyze videos for regulatory compliance
- **HealthScribe**: Medical transcription using AWS HealthScribe
- **Differential Diagnosis (DDx) Assistant**: Get assistance with clinical diagnosis
- **Excel Formula Generator AI Assistant**: Get assistance with Excel Formulas
- **Medical Bill Extractor**: Extract and analyze data from medical bills

## Installation

```sh
 pip install newberryai
```
## Usage

You can use the command-line interface:

```
newberryai <command> [options]
```

Available commands:
- `compliance` - Run compliance check on medical videos
- `healthscribe` - Transcribe medical conversations
- `ddx` - Get differential diagnosis assistance
- `ExcelO` - Get excel formula AI assistance
- `bill_extract` - Extract and analyze medical bill data

#### Compliance Checker

```sh
newberryai compliance --video_file /path/to/video.mp4 --question "Is the video compliant with safety regulations such as mask?"
```

#### HealthScribe

```sh
newberryai healthscribe --file_path conversation.wav \
                       --job_name myJob \
                       --data_access_role_arn arn:aws:iam::aws_accountid:role/your-role \
                       --input_s3_bucket my-input-bucket \
                       --output_s3_bucket my-output-bucket \
                       --s3_key s3-key
```

#### Differential Diagnosis Assistant

```sh
# With a specific clinical indication
newberryai ddx --clinical_indication "Patient presents with fever, cough, and fatigue for 5 days"

# Interactive CLI mode
newberryai ddx --interactive

# Launch Gradio web interface
newberryai ddx --gradio
```

#### Excel Formula Assistant

```sh
# With a specific Excel Query
newberryai ExcelO --Excel_query "Calculate average sales for products that meet specific criteria E.g: give me excel formula to calculate average of my sale for year 2010,2011 sales is in col A, Year in Col B  and Months in Col C"

# Interactive CLI mode
newberryai ExcelO --interactive

# Launch Gradio web interface
newberryai ExcelO --gradio
```


#### Medical Bill Extractor

```sh
# Analyze a specific document
newberryai bill_extract --image_path /path/to/medical_bill.pdf

# Interactive CLI mode
newberryai bill_extract --interactive

# Launch Gradio web interface
newberryai bill_extract --gradio
```

### Python Module

You can also use NewberryAI as a Python module in your applications.

#### HealthScribe

```python
from newberryai import HealthScribe
import os
import newberryai

# Set the environment variables for the AWS SDK
os.environ['AWS_ACCESS_KEY_ID'] = 'your_aws_access_key_id'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'your_aws_secret_access_key'
os.environ['AWS_REGION'] = 'your_aws_region'

# Initialize the client
scribe = HealthScribe(
    input_s3_bucket="input-bucket",
    data_access_role_arn="arn:aws:iam::12345678912:role/your_role"
)

# Process an audio file
result = scribe.process(
    file_path="/path/to/audio_file.mp3",
    job_name="test_job_1",
    output_s3_bucket="output-bucket"
)

# Use the summary
print(result.summary)
```

#### Compliance Checker

```python
from newberryai import ComplianceChecker

checker = ComplianceChecker()
video_file = "/path/to/video.mp4"
compliance_question = "Is the video compliant with safety regulations such as mask?"

# Call the compliance-checker function
result, status_code = checker.check_compliance(
    video_file=video_file,
    question=compliance_question
)

# Check for errors
if status_code:
    print(f"Error: {result.get('error', 'Unknown error')}")
else:
    # Print the compliance check result
    print(f"Compliant: {'Yes' if result['compliant'] else 'No'}")
    print(f"Analysis: {result['analysis']}")
```

#### Differential Diagnosis Assistant

```python
from newberryai import DDxChat

# Initialize the DDx Assistant
ddx_chat = DDxChat()

# Ask a specific clinical question
response = ddx_chat.ask("Patient presents with fever, cough, and fatigue for 5 days")
print(response)

# Alternatively, launch interactive CLI
# ddx_chat.run_cli()

# Or launch the Gradio web interface
# ddx_chat.start_gradio()
```
#### Excel Formual Genenrator AI Assistant

```python
from newberryai import ExcelExp

# Initialize the DDx Assistant
excel_expert = ExcelExp()

# Ask a specific clinical question
response = excel_expert.ask("Calculate average sales for products that meet specific criteria E.g: give me excel formula to calculate average of my sale for year 2010,2011 sales is in col A, Year in Col B  and Months in Col C")
print(response)

# Alternatively, launch interactive CLI
# excel_expert.run_cli()

# Or launch the Gradio web interface
# excel_expert.start_gradio()
```


#### Medical Bill Extractor

```python
from newberryai import Bill_extractor

# Initialize the Bill Extractor
extractor = Bill_extractor()

# Analyze a document
analysis = extractor.analyze_document("/path/to/medical_bill.pdf")
print(analysis)

# Alternatively, launch interactive CLI
# extractor.run_cli()

# Or launch the Gradio web interface
# extractor.start_gradio()
```

## Requirements

- Python 3.8+
- AWS account with appropriate permissions
- Required AWS services:
  - Amazon S3
  - AWS HealthScribe
  - AWS IAM

## AWS Configuration

To use the AWS-powered features, you need to set up the following:

1. An AWS account with appropriate permissions
2. AWS IAM role with access to required services
3. S3 buckets for input and output data
4. AWS credentials configured in your environment

## License

This project is licensed under the MIT License.
