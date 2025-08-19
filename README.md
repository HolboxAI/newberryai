# 🫐📦 **NewberryAI**

<p>
  <a href="https://github.com/HolboxAI/newberryai">
    <img src="https://img.shields.io/badge/GitHub-HolboxAI%2Fnewberryai-blue?logo=github&style=flat-square" alt="GitHub Repo">
  </a>
  <a href="https://pypi.org/project/newberryai/">
    <img src="https://img.shields.io/pypi/v/newberryai?style=flat-square" alt="PyPI">
  </a>
  <a href="https://pypistats.org/packages/newberryai">
    <img src="https://img.shields.io/pypi/dm/newberryai?style=flat-square" alt="PyPI - Downloads">
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/pypi/l/newberryai?style=flat-square" alt="License">
  </a>
  <a href="https://github.com/HolboxAI/newberryai/stargazers">
    <img src="https://img.shields.io/github/stars/HolboxAI/newberryai?style=flat-square" alt="GitHub stars">
  </a>
</p>


# NewberryAI 

**The complete AI toolkit that turns complex workflows into simple Python commands. From medical diagnosis to compliance checking, document analysis to face recognition - NewberryAI brings enterprise-grade AI capabilities to your fingertips.**

---

## Installation

```bash
pip install newberryai
```

### Troubleshooting Installation Issues
## If you encounter issues installing pyaudio or related audio dependencies, try the following:

 # For Ubuntu/Debian systems:
 ```bash
bashsudo apt-get install -y portaudio19-dev
pip install pyaudio
```
## For other systems:

# macOS: 
```bash 
brew install portaudio then pip install pyaudio
```
# Windows: 
Download pre-compiled wheels from 
"https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio"
and 
```bash 
pip install PyAudio‑0.2.11‑cp312‑cp312‑win_amd64.whl
```
 ***replace the filename with the one you downloaded***

## 📚Features

### 🏥 Healthcare & Medical
- **HealthScribe**: Medical transcription with AWS HealthScribe
- **Differential Diagnosis Assistant(DDX)**: Clinical diagnosis support
- **Medical Bill Extractor**: Automated medical billing analysis
- **EDI 835 Generator**: Generate EDI 835 files from medical documents
- **MedicalClaimVerifier**:Predicts insurance claim approval likelihood from medical documents 

### 🔒 Compliance & Security
- **Compliance Checker**: Video analysis for regulatory compliance
- **PII Redactor**: Remove personally identifiable information
- **PII Extractor**: Extract and categorize sensitive data

### 📊 Data & Analytics
- **EDA Assistant**: Automated exploratory data analysis
- **NL2SQL**: Natural language to SQL query conversion
- **Excel Formula Generator**: AI-powered Excel formula creation

### 📄 Document Processing
- **PDF Summarizer**: Intelligent document summarization
- **PDF Extractor**: Semantic search and content extraction
- **Handwriting to Text Converter**: Extract handwritten text from images using AI

### 🎨 Media Generation
- **Video Generator**: Text-to-video with Amazon Bedrock Nova
- **Image Generator**: Text-to-image with Titan Image Generator
- **Virtual Try-On**: AI-powered fashion visualization

### 🔍 Computer Vision
- **Face Recognition**: Identity management with AWS Rekognition
- **Face Detection**: Video face detection and tracking


### 💻 Development Tools
- **Coding Assistant**: Code review and debugging support
- **Speech-to-Speech**: Real-time voice interaction

## 1. Compliance Checker

### Environment Setup
```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1
```

### Python SDK
```python
#Analyze videos for regulatory compliance. Requires AWS credentials.
from newberryai import ComplianceChecker

checker = ComplianceChecker()
video_file = 'YOUR.mp4'
compliance_question = 'Is the video compliant with safety regulations such as mask?'

result, status_code = checker.check_compliance(
    video_file=video_file,
    prompt=compliance_question
)
if status_code:
    print(f'Error: {result.get("error", "Unknown error")})')
else:
    print(f'Compliant: {"Yes" if result["compliant"] else "No"}')
    print(f'Analysis: {result["analysis"]}')
```

### CLI Usage
```sh
newberryai compliance --video_file YOUR.mp4 --question "Is the video compliant with safety regulations such as mask?"
newberryai compliance --gradio
```

---

## 2. HealthScribe

### Environment Setup
```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1
HEALTHSCRIBE_INPUT_BUCKET=your-healthscribe-input-bucket
HEALTHSCRIBE_OUTPUT_BUCKET=your-healthscribe-output-bucket
HEALTHSCRIBE_DATA_ACCESS_ROLE=arn:aws:iam::account:role/your-role
```

### Python SDK
```python
# Medical transcription using AWS HealthScribe. Requires AWS credentials.
from newberryai import HealthScribe
scribe = HealthScribe(
    input_s3_bucket='your-input-bucket',
    data_access_role_arn='arn:aws:iam::992382417943:role/YOUR-role'
)
result = scribe.process(
    file_path=r'YOUR_AUDIO.mp3',
    job_name='JOB-NAME',
    output_s3_bucket='your-output-bucket'
)
print(result["summary"])
```

### CLI Usage
```sh
newberryai healthscribe --file_path YOUR_AUDIO.mp3 --job_name sdktest --output_s3_bucket dax-healthscribe-v2
newberryai healthscribe --gradio
```

---

## 3. Differential Diagnosis (DDx) Assistant

### Environment Setup
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
```

### Python SDK
```python
#Get assistance with clinical diagnosis.
from newberryai import DDxChat

ddx_chat = DDxChat()
response = ddx_chat.ask('Patient presents with fever, cough, and fatigue for 5 days')
print(response)
```

### CLI Usage
```sh
newberryai ddx --question "Patient presents with fever, cough, and fatigue for 5 days"
newberryai ddx --interactive
newberryai ddx --gradio
```

---

## 4. Excel Formula Generator AI Assistant

# Environment Setup
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
```

### Python SDK
```python
#Get assistance with Excel formulas.
from newberryai import ExcelExp

excel_expert = ExcelExp()
response = excel_expert.ask(
"Calculate average sales for products that meet specific criteria E.g: give me excel formula to calculate average of my sale for year 2010,2011 sales is in col A, Year in Col B  and Months in Col C"
)
print(response)
```

### CLI Usage
```sh
newberryai ExcelO --Excel_query "Calculate average sales for products that meet specific criteria E.g: give me excel formula to calculate average of my sale for year 2010,2011 sales is in col A, Year in Col B  and Months in Col C"
newberryai ExcelO --interactive
newberryai ExcelO --gradio
```

---

## 5. Medical Bill Extractor

### Environment Setup
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
# AWS Credentials
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
```

### Python SDK
```python
#Extract and analyze data from medical bills.
from newberryai import Bill_extractor

extractor = Bill_extractor()
analysis = extractor.analyze_document('Billimg.jpg')
print(analysis)
```

### CLI Usage
```sh
newberryai bill_extract --file_path Billimg.jpg
newberryai bill_extract --interactive
newberryai bill_extract --gradio
```

---

## 6. Coding and Debugging AI Assistant

### Environment Setup
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
```

### Python SDK
```python
#Analyze code and help you with coding as debugger.
from newberryai import CodeReviewAssistant

code_debugger = CodeReviewAssistant()
response = code_debugger.ask('''Explain and correct below code
def calculate_average(nums):
sum = 0
for num in nums:
sum += num
average = sum / len(nums)
return average

numbers = [10, 20, 30, 40, 50]
result = calculate_average(numbers)
print("The average is:", results)''')
print(response)
```

### CLI Usage
```sh
newberryai Coder --code_query "Explain and correct below code

def calculate_average(nums):
    sum = 0
    for num in nums:
        sum += num
    average = sum / len(nums)
    return average

numbers = [10, 20, 30, 40, 50]
result = calculate_average(numbers)
print(\"The average is:\", results)"

newberryai Coder --interactive
newberryai Coder --gradio
```

---

## 7. PII Redactor AI Assistant

### Environment Setup
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
```

### Python SDK
```python
#Analyze text and remove PII (personally identifiable information) from the text.
from newberryai import PII_Redaction

pii_red = PII_Redaction()
response = pii_red.ask("Patient name is John Doe with fever. he is from Austin,Texas.His email id is john.doe14@email.com")
print(response)
```

### CLI Usage
```sh
newberryai PII_Red --text "Patient name is John Doe with fever. he is from Austin,Texas.His email id is john.doe14@email.com"
newberryai PII_Red --interactive
newberryai PII_Red --gradio
```

---

## 8. PII Extractor AI Assistant

### Environment Setup
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
```

### Python SDK
```python
#Analyze text and extract PII (personally identifiable information) from the text.
from newberryai import PII_extraction

pii_extract = PII_extraction()
response = pii_extract.ask("Patient name is John Doe with fever. he is from Austin,Texas.His email id is john.doe14@email.com")
print(response)
```

### CLI Usage
```sh
newberryai PII_extract --text "Patient name is John Doe with fever. he is from Austin,Texas.His email id is john.doe14@email.com"
newberryai PII_extract --interactive
newberryai PII_extract --gradio
```

---

## 9. EDA AI assistant

### Environment Setup
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
```

### Python SDK
```python
# Perform detailed data exploration with real statistics, hypothesis testing, actionable insights, and visualizations—no code, just direct analysis

from newberryai import EDA
import pandas as pd

eda = EDA()
eda.current_data = pd.read_csv(r'your_csv.csv')

# Ask questions about your data
response = eda.ask("What is the average value of column 'xyz'?")
print(response)

# Generate visualizations (distribution, correlation, categorical, time series)
# Show all visualizations:
eda.visualize_data()
# Show only distribution plots:
eda.visualize_data(plot_type="dist")
# Show only correlation heatmap:
eda.visualize_data(plot_type="corr")
# Show only categorical plots:
eda.visualize_data(plot_type="cat")
# Show only time series plots:
eda.visualize_data(plot_type="time")
```

### CLI Usage
```sh
newberryai eda --file_path your_csv.csv --question "What is the average value of column 'target'?"
newberryai eda --interactive
newberryai eda --gradio

# Visualization commands (in interactive CLI):
#   visualize or viz           # Show all visualizations
#   visualize dist or viz dist # Show distribution plots
#   visualize corr or viz corr # Show correlation heatmap
#   visualize cat or viz cat   # Show categorical plots
#   visualize time or viz time # Show time series plots
```

---

## 10. PDF Document Summarizer

### Environment Setup
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
```

### Python SDK
```python
#Extract and summarize content from PDF documents.
from newberryai import DocSummarizer

summarizer = DocSummarizer()
response = summarizer.ask(r'YOUR-pdf.pdf')
print(response)
```

### CLI Usage
```sh
newberryai pdf_summarizer --file_path YOUR-pdf.pdf
newberryai pdf_summarizer --interactive
newberryai pdf_summarizer --gradio
```

---

## 11. PDF Extractor

### Environment Setup
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
```

### Python SDK
```python
#Extract and query content from PDF documents using embeddings and semantic search. (Async usage)

import asyncio
from newberryai import PDFExtractor

async def pdf_extract_demo():
    extractor = PDFExtractor()
    pdf_id = await extractor.process_pdf(r'YOUR-pdf.pdf')
    response = await extractor.ask_question(pdf_id, 'What is the mode of review in the document?')
    print(response['answer'])
    print("\nSource Chunks:")
    for chunk in response['source_chunks']:
        print(f"\n---\n{chunk}")

#To run the async demo in a notebook cell:
await pdf_extract_demo()
```

### CLI Usage
```sh
newberryai pdf_extract --file_path YOUR-pdf.pdf --question "What is the mode of review in the document?"
newberryai pdf_extract --interactive
newberryai pdf_extract --gradio
```

---

## 12. Video Generator

### Environment Setup
```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
BEDROCK_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.nova-canvas-v1:0
```

### Python SDK
```python
#Generate videos from text using Amazon Bedrock's Nova model. Requires AWS credentials.
# Example usage
from newberryai import VideoGenerator
generator = VideoGenerator()
prompt = "A cat dancing on a wall"
async def run_video():
    response = await generator.generate(
        text=prompt,
        duration_seconds=6,
        fps=24,
        dimension="1280x720",
        seed=42
    )
    print(response["message"])
    print("Waiting for video to complete...")
    final_response = await generator.wait_for_completion(response["job_id"])
    print(final_response["message"])
    print(f"Video URL: {final_response['video_url']}")
await run_video()
```

### CLI Usage
```sh
newberryai video --text "A cat dancing on a wall" --duration 6 --fps 24 --dimension 1280x720 --seed 42
newberryai video --interactive
newberryai video --gradio
```

---

## 13. Image Generator

### Environment Setup
```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
BEDROCK_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.titan-image-generator-v1
```

### Python SDK
```python
from newberryai.image_generator import ImageGenerator
import asyncio

generator = ImageGenerator()
prompt = "A lotus in a pond"
result = await generator.generate(
    text= prompt,
    width=512,
    height=512,
    number_of_images=1,
    cfg_scale=8,
    seed=42,
    quality="standard"
)

print(result["message"])
for path in result["images"]:
    print(f"Generated image path: {path}")
```

### CLI Usage
```sh
newberryai image --text "A lotus in a pond" --width 512 --height 512 --number_of_images 1 --cfg_scale 8 --seed 42 --quality standard
newberryai image --interactive
newberryai image --gradio
```

---

## 14. Face Recognition

### Environment Setup
```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
REKOGNITION_COLLECTION_ID=your-collection-id
REKOGNITION_REGION=us-east-1
```

### Python SDK
```python
# Import the FaceRecognition class
from newberryai import FaceRecognition

# Initialize face recognition
face_recognition = FaceRecognition()

# Add a face to the collection and recognize a face in one go
add_response = face_recognition.add_to_collect("yourimg.jpeg", "Name")
print(add_response["message"], f"Face ID: {add_response.get('face_id', 'N/A')}")

# Recognize a face from another image
recognize_response = face_recognition.recognize_image("yourimg2.jpeg")
print(recognize_response["message"])
if recognize_response["success"]:
    print(f"Recognized: {recognize_response['name']} (Confidence: {recognize_response['confidence']:.2f}%)")
```

### CLI Usage
```sh
newberryai face_recognig --image_path yourimg.jpeg --add --name Name
newberryai face_recognig --image_path yourimg2.jpeg
newberryai face_recognig --interactive
newberryai face_recognig --gradio
```

---

## 15. Face Detection

### Environment Setup
```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
REKOGNITION_COLLECTION_ID=your-collection-id
REKOGNITION_REGION=us-east-1
```

### Python SDK
```python
# Import and initialize FaceDetection class
from newberryai.face_detection import FaceDetection
face_detector = FaceDetection()

# Add face to collection
add_response = face_detector.add_face_to_collection("yourimg.jpeg", "kirti")
print(add_response["message"])
if add_response["success"]:
    print(f"Face ID: {add_response['face_id']}")

# Process video
results = face_detector.process_video("yourvideo.mp4", max_frames=20)
for detection in results:
    print(f"\nTimestamp: {detection['timestamp']}s")
    if detection.get('external_image_id'):
        print(f"Matched Face: {detection['external_image_id']}")
        print(f"Face ID: {detection['face_id']}")
        print(f"Confidence: {detection['confidence']:.2f}%")
    else:
        print("No match found in collection")
```

### CLI Usage
```sh
newberryai face_detect --add_image yourimg.jpeg --name kirti
newberryai face_detect --video_path yourvideo.mp4 --max_frames 20
newberryai face_detect --interactive
newberryai face_detect --gradio
```

---

## 16. NL2SQL

### Environment Setup
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
# Database Configuration
DB_HOST=localhost
DB_USER=your_db_username
DB_PASSWORD=your_db_password
DB_NAME=your_database_name
DB_PORT=3306
```

### Python SDK
```python
#Natural Language to SQL Query Assistant
# Import the NL2SQL class
from newberryai import NL2SQL
import json
# Initialize NL2SQL processor
nl2sql = NL2SQL()

# Set up the database connection parameters (adjust these accordingly)
host = "127.0.0.1"
user = "user-name"
password = "passward"
database = "your-database-name"
port = 3306

# Connect to the database
nl2sql.connect_to_database(host, user, password, database, port)

# Test a natural language question to SQL conversion
question = "Show all tables"
response = nl2sql.process_query(question)

# Print the results: SQL query, data, and summary
if response["success"]:
    print(f"Generated SQL Query: {response['sql_query']}")
    print(f"Data: {json.dumps(response['data'], indent=2)}")
    print(f"Summary: {response['summary']}")
else:
    print(f"Error: {response['message']}")
```

### CLI Usage
```sh
newberryai nl2sql --question "Show all tables" --user user-name --password passward --database your-database-name
newberryai nl2sql --interactive
newberryai nl2sql --gradio
```

---

## 17. Virtual Try-On

### Environment Setup
```bash
# Fashn API Configuration
FASHN_API_KEY=your_fashn_api_key
FASHN_API_URL=https://api.fashn.ai/v1
```

### Python SDK
```python
# Generate virtual try-on images using AI. Requires Fashn API credentials.
import base64
import asyncio
from newberryai import VirtualTryOn
try_on = VirtualTryOn()
request = await try_on.process(
    model_image='model.jpg',
    garment_image='image.png',
    category='tops'
)
async def tryon_demo():
    job_id = request["job_id"]
    while True:
        status = await try_on.get_status(job_id)
        if status["status"] in ['completed', 'failed']:
            break
        await asyncio.sleep(3)
    if status["status"] == "completed" and status["output"]:
        print('Generated images:')
        for url in status["output"]:
            print(url)
# Run the demo
await tryon_demo()
```

### CLI Usage
```sh
newberryai tryon --model_image model.jpg --garment_image image.png --category tops
newberryai tryon --interactive
newberryai tryon --gradio
```

---

## 18. Speech-to-Speech

### Environment Setup
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
```

### Python SDK
```python
# Real-time voice interaction with an AI assistant.
from newberryai.speechtospeech import RealtimeApp

# Ensure you have set your OPENAI_API_KEY environment variable
# and installed necessary audio drivers and dependencies (`pip install "openai[realtime]"`).
app = RealtimeApp()
app.run()
```

### CLI Usage
```sh
newberryai speech_to_speech
```

---

## 19. Handwriting to Text Converter

### Environment Setup
```bash
# AWS Credentials (for S3 access or AWS-powered features)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1
```

### Python SDK
```python
# Extract handwritten text from an image using AI.
from newberryai import Handwrite2Text

# Initialize the handwriting-to-text converter
handwriter = Handwrite2Text()

# Path to your handwritten document image
image_path = 'handwritten_note.jpg'

# Extract handwritten text from the image
extracted_text = handwriter.extract_text(image_path)

print("Extracted Handwritten Text:")
print(extracted_text)
```

### CLI Usage
```sh
newberryai handwrite2text --file_path handwritten_note.jpg
newberryai handwrite2text --gradio
```

---

## 20. Image Search 

### Environment Setup
```bash
# AWS Credentials (for S3 access)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1
```

### How it works
- Upload your images to your S3 bucket (using AWS Console, CLI, or script).
- Build the index using the CLI or Python API (this creates a local FAISS index from your S3 images, using Amazon Titan Multimodal Embeddings G1 for all embeddings).
- Search images using natural language (text-to-image, powered by Titan text embeddings) or by image (image-to-image, powered by Titan image embeddings) via CLI, Gradio, or Python API.

### Python SDK
```python
from newberryai import ImageSearch
from PIL import Image

# Initialize with your S3 bucket name
searcher = ImageSearch(s3_bucket='your-bucket-name')

# Build the index (create FAISS index from S3 images)
searcher.build_index(prefix='optional/folder/')

# Search for images by text
results = searcher.search('A cat sitting on a sofa', k=5)
for r in results:
    print(r['image_url'], r['distance'], r['folder'])

# Search for images by image
query_image = Image.open('query.jpg')
results = searcher.search_by_image(query_image, k=5)
for r in results:
    print(r['image_url'], r['distance'], r['folder'])
```

### CLI Usage
```sh
# Build the index from your S3 images
newberryai img_search --s3_bucket your-bucket-name --build_index

# Search via CLI (choose text or image search at prompt)
newberryai img_search --s3_bucket your-bucket-name --cli

# Launch Gradio UI (text and image search, with tabs)
newberryai img_search --s3_bucket your-bucket-name --gradio
```

**Note:** You must upload your images to S3 before building the index. The tool does not upload images for you.

---

## 21. EDI Generator

NewberryAI supports generating three major EDI formats from medical documents:
- **EDI 835**: Electronic Remittance Advice (payment/remittance details)
- **EDI 837**: Health Care Claim (claim submission)
- **EDI 270**: Eligibility Inquiry (insurance eligibility check)

You can generate any of these by selecting the appropriate extractor or CLI command.

### Environment Setup
```bash
# AWS Credentials (required for Bedrock/Claude model)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1
```

### Python SDK
```python
from newberryai import EDIGenerator

# EDI 835: Remittance Advice
era = EDIGenerator("835")
edi_835_output = era.analyze_document('your_medical_bill_or_remittance.pdf')
print(edi_835_output)

# EDI 837: Health Care Claim
claim = EDIGenerator("837")
edi_837_output = claim.analyze_document('your_medical_visit_summary.pdf')
print(edi_837_output)

# EDI 270: Eligibility Inquiry
elig = EDIGenerator("270")
edi_270_output = elig.analyze_document('your_patient_insurance_details.pdf')
print(edi_270_output)
```

### CLI Usage
```sh
# EDI 835 (Remittance Advice)
newberryai edi835 --file_path your_medical_bill_or_remittance.pdf
newberryai edi835 --interactive
newberryai edi835 --gradio

# EDI 837 (Health Care Claim)
newberryai edi837 --file_path your_medical_visit_summary.pdf
newberryai edi837 --interactive
newberryai edi837 --gradio

# EDI 270 (Eligibility Inquiry)
newberryai edi270 --file_path your_patient_insurance_details.pdf
newberryai edi270 --interactive
newberryai edi270 --gradio
```

- Upload a relevant medical document (image or PDF).
- The AI will extract required data and generate a valid EDI file as plain text (no JSON, no markdown).
- If required data is missing, placeholder values will be used in the EDI output.
- Output is ready to save as `.edi` or `.txt`.

---
## 22. Medical Claim Verifier

### Environment Setup
```bash
# OpenAI Configuration (for LLM-powered analysis)
OPENAI_API_KEY=your_openai_api_key
# AWS Credentials (for EDI generation and document processing)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1
```

### Python SDK
```python
from newberryai import MedicalClaimVerifier

# Initialize the verifier
verifier = MedicalClaimVerifier()

# Verify a claim from a medical document (PDF/Image/Text)
# When to use:
# - A patient brings in a medical bill from another provider
# - You have scanned medical documents
# - You want to verify claims before submitting to insurance

result = verifier.verify_claim_from_document(
    file_path='your_claim_document.pdf', 
    insurance_provider='Blue Cross Blue Shield'
)

# Get results
print(f"Approval Likelihood: {result['approval_prediction']['likelihood']}")
print(f"Risk Factors: {result['risk_factors']}")
print(f"Recommendations: {result['recommendations']}")
```



### CLI Usage
```sh
# Verify a claim from a document
newberryai claim_verifier --file_path your_claim_document.pdf --insurance_provider "Blue Cross Blue Shield"

# Launch Gradio interface
newberryai claim_verifier --gradio

# Run in interactive CLI mode
newberryai claim_verifier --interactive
```

---
## 23. GPT Features

#### Environment Setup

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1
```

```python
# Feature GPT-5 Summarizer
from newberryai import FeatureGptSummarizer
summarizer = FeatureGptSummarizer()
summary = summarizer.ask(file_path="path_to_your_pdf_document.pdf")
print(summary)

# Feature GPT-5 Chat Assistant
from newberryai import FeatureGptChat
chat_assistant = FeatureGptChat()
response = chat_assistant.ask("Hello! How can I assist you today?")
print(response)

# Feature GPT-5 Image Analyzer
from newberryai import FeatureGptImage
image_analyzer = FeatureGptImage()
response = image_analyzer.ask(file_path="path_to_your_image.jpg")
print(response)

# Feature GPT-5 Agent
from newberryai import FeatureGptAgent
agent = FeatureGptAgent()
response = agent.ask("Solve this problem: 12 * 15")
print(response)
```

### CLI Usage
```sh
# Feature GPT-5 Summarizer
newberryai feature_gpt5_summarizer --file_path YOUR_DOCUMENT.pdf --gradio
newberryai feature_gpt5_summarizer --interactive

# Feature GPT-5 Chat Assistant
newberryai feature_gpt5_chat --message "Hello, assistant!" --gradio
newberryai feature_gpt5_chat --interactive

# Feature GPT-5 Image Analyzer
newberryai feature_gpt5_image --file_path YOUR_IMAGE.png --gradio
newberryai feature_gpt5_image --interactive

# Feature GPT-5 Agent
newberryai feature_gpt5_agent --instruction "Solve this math problem: 12 * 15" --gradio
newberryai feature_gpt5_agent --interactive

```
