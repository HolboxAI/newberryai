# NewberryAI

A Python package for AI tools using LLM.

## Overview

- **Compliance Checker**: Analyze videos for regulatory compliance
- **HealthScribe**: Medical transcription using AWS HealthScribe
- **Differential Diagnosis (DDx) Assistant**: Get assistance with clinical diagnosis
- **Excel Formula Generator AI Assistant**: Get assistance with Excel Formulas
- **Medical Bill Extractor**: Extract and analyze data from medical bills
- **Coding Assistant**: Analyze code and help you with coding as debugger
- **Speech to speech assistant**: Real-time voice interactive assistant
- **PII Redactor AI assistant**: Analyze text and remove PII (personally identifiable information) from the text
- **PII extractor AI assistant**: Analyze text and extract PII (personally identifiable information) from the text
- **EDA AI assistant**: Perform detailed data exploration with real statistics, hypothesis testing, and actionable insights—no code, just direct analysis.
- **PDF Summarizer**: Extract and summarize content from PDF documents

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
- `coder` - Analyze code and help you with coding as debugger
- `speech_to_speech` - Launch the real-time Speech-to-Speech assistant.
- `PII_Red` - Analyze text and remove PII from the text using AI.
- `PII_extract` - Analyze text and extract PII from the text using AI.

### CLI Tool

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
newberryai bill_extract --file_path /path/to/medical_bill.jpeg

# Interactive CLI mode
newberryai bill_extract --interactive

# Launch Gradio web interface
newberryai bill_extract --gradio
```
#### Python Coding Assistant

```sh
# With a specific python coding Query
newberryai coder --code_query " your Query related to your python code"

# Interactive CLI mode
newberryai coder --interactive

# Launch Gradio web interface
newberryai coder --gradio
```
#### PII Redactor AI Assistant

```sh
# With a specific Text
newberryai PII_Red --text " your text containing PII."

# Interactive CLI mode
newberryai PII_Red --interactive

# Launch Gradio web interface
newberryai PII_Red --gradio
```
#### PII Extractor AI Assistant

```sh
# With a specific Text
newberryai PII_extract --text " your text containing PII."

# Interactive CLI mode
newberryai PII_extract --interactive

# Launch Gradio web interface
newberryai PII_extract --gradio
```
#### Speech to Speech Assitant

```sh
# Launch the real-time speech-to-speech application
newberryai speech_to_speech
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
analysis = extractor.analyze_document("/path/to/medical_bill.jpeg")
print(analysis)

# Alternatively, launch interactive CLI
# extractor.run_cli()

# Or launch the Gradio web interface
# extractor.start_gradio()
```
#### Coding and Debugging AI Assistant

```python
from newberryai import CodeReviewAssistant

# Initialize the DDx Assistant
code_debugger = CodeReviewAssistant()

# Ask a specific clinical question
response = code_debugger.ask("""Explain and correct below code
def calculate_average(nums):
sum = 0
for num in nums:
sum += num
average = sum / len(nums)
return average

numbers = [10, 20, 30, 40, 50]
result = calculate_average(numbers)
print(“The average is:”, results)""")
print(response)

# Alternatively, launch interactive CLI
# code_debugger.run_cli()

# Or launch the Gradio web interface
# code_debugger.start_gradio()
```
#### Speech-to-Speech Assistant
```python
from newberryai import RealtimeApp

# Initialize and run the speech-to-speech assistant
app = RealtimeApp()
app.run()
```
#### PII Redactor AI Assistant

```python
from newberryai import PII_Redaction

# Initialize the PII Redactor Assistant
pii_red = PII_Redaction()

# Provide a text to detect PII
response = pii_red.ask("Patient name is John Doe with fever. he is from Austin,Texas.His email id is john.doe14@email.com")
print(response)

# Alternatively, launch interactive CLI
# pii_red.run_cli()

# Or launch the Gradio web interface
# pii_red.start_gradio()
```
#### PII extractor AI Assistant

```python
from newberryai import PII_extraction

# Initialize the PII Extraction Assistant
pii_extract = PII_extraction()

# Provide a text to detect PII
response = pii_extract.ask("Patient name is John Doe with fever. he is from Austin,Texas.His email id is john.doe14@email.com")
print(response)

# Alternatively, launch interactive CLI
# pii_extract.run_cli()

# Or launch the Gradio web interface
# pii_extract.start_gradio()
```
#### PDF Document Summarizer

```python
from newberryai import DocSummarizer

# Initialize the PDF Summarizer
summarizer = DocSummarizer()

# Summarize a specific document
response = summarizer.ask("/path/to/your/document.pdf")
print(response)

# Alternatively, launch interactive CLI
# summarizer.run_cli()

# Or launch the Gradio web interface
# summarizer.start_gradio()
```
#### EDA - Exploratory Data Analysis
```python
from newberryai import EDA
eda = EDA()

# Load your dataset (set current_data manually if needed)
import pandas as pd
eda.current_data = pd.read_csv("/path/to/your/data.csv")

# Ask your analysis question (e.g. descriptive statistics, hypothesis testing)
response = eda.ask("What is the average value of column 'Sales'?")
print(response)

# Generate visualizations (distribution, correlation, categorical, time series)
eda.visualize_data("dist")  # distribution plots
eda.visualize_data("corr")  # correlation heatmap
eda.visualize_data("cat")   # categorical distributions
eda.visualize_data("time")  # time series plots if datetime present

# Alternatively, start CLI for interactive session
# eda.run_cli()

# Or launch Gradio interface
# eda.start_gradio()

```
#### CLI Usage for PDF Summarizer

```sh
# With a specific document
newberryai pdf_summarizer --code /path/to/your/document.pdf

# Interactive CLI mode
newberryai pdf_summarizer --interactive

# Launch Gradio web interface
newberryai pdf_summarizer --gradio
```
#### CLI Usage for EDA 

``` sh
 #Analyze a CSV file interactively

newberryai eda --file_path /path/to/your/data.csv --interactive

 #Launch Gradio web interface
newberryai eda --file_path /path/to/your/data.csv --gradio

#Generate visualizations (after loading a file)
newberryai eda --file_path /path/to/your/data.csv --visualize
#### Troubleshooting: SSL Certificate Issues
If you encounter SSL certificate errors while running NewberryAI, you can fix them by running:
```sh
pip install --upgrade certifi
export SSL_CERT_FILE=$(python -c "import certifi; print(certifi.where())")
```
This ensures that your system is using the latest SSL certificates.



---
###  Setting Up OpenAI API Key for Speech-to-Speech

To use OpenAI's Speech-to-Speech features, you need to set your API key as an environment variable.

#### Step-by-Step:

1. **Get your API key** from [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)

2. **Set the environment variable** in your terminal or shell configuration file.

##### For **bash** or **zsh** (macOS/Linux):
```bash
export OPENAI_API_KEY="your-api-key-here"
```

You can add this line to your `~/.bashrc`, `~/.bash_profile`, or `~/.zshrc` file to make it permanent.

##### For **Windows (Command Prompt)**:
```cmd
set OPENAI_API_KEY=your-api-key-here
```

##### For **Windows (PowerShell)**:
```powershell
$env:OPENAI_API_KEY="your-api-key-here"
```

3. **Verify** it's set by running:
```bash
echo $OPENAI_API_KEY
```


## Requirements

- Python 3.8+
- OpenAI account with Api keys
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
