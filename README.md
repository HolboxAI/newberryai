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
newberryai excel --question "Calculate average sales for products that meet specific criteria E.g: give me excel formula to calculate average of my sale for year 2010,2011 sales is in col A, Year in Col B  and Months in Col C"
newberryai excel --interactive
newberryai excel --gradio
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
newberryai bill --file_path Billimg.jpg
newberryai bill --interactive
newberryai bill --gradio
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
newberryai code --question "Explain and correct below code
def calculate_average(nums):
sum = 0
for num in nums:
sum += num
average = sum / len(nums)
return average

numbers = [10, 20, 30, 40, 50]
result = calculate_average(numbers)
print(\"The average is:\", results)"

newberryai code --interactive
newberryai code --gradio
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
newberryai pii --text "Patient name is John Doe with fever. he is from Austin,Texas.His email id is john.doe14@email.com"
newberryai pii --interactive
newberryai pii --gradio
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
newberryai pii --text "Patient name is John Doe with fever. he is from Austin,Texas.His email id is john.doe14@email.com"
newberryai pii --interactive
newberryai pii --gradio
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
#Perform detailed data exploration with real statistics, hypothesis testing, and actionable insights—no code, just direct analysis

from newberryai import EDA
import pandas as pd

eda = EDA()
eda.current_data = pd.read_csv(r'your_csv.csv')

response = eda.ask("What is the average value of column 'xyz'?")
print(response)
```

### CLI Usage
```sh
newberryai eda --file_path your_csv.csv --question "What is the average value of column 'target'?"
newberryai eda --interactive
newberryai eda --gradio
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
newberryai doc --file_path YOUR-pdf.pdf --question "Extract and summarize content from PDF documents."
newberryai doc --interactive
newberryai doc --gradio
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
newberryai pdf --file_path YOUR-pdf.pdf --question "What is the mode of review in the document?"
newberryai pdf --interactive
newberryai pdf --gradio
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
newberryai video --text "A cat dancing on a wall" --duration_seconds 6 --fps 24 --dimension 1280x720 --seed 42
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
newberryai face --image_path yourimg.jpeg --name Name
newberryai face --image_path yourimg2.jpeg --recognize
newberryai face --interactive
newberryai face --gradio
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
newberryai face --image_path yourimg.jpeg --add_to_collection
newberryai face --video_path yourvideo.mp4 --max_frames 20
newberryai face --interactive
newberryai face --gradio
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
newberryai sql --question "Show all tables"
newberryai sql --interactive
newberryai sql --gradio
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

## ⚙️Requirements

- Python 3.8+
- AWS Account (for AWS-powered features)
- OpenAI API key
- Additional API keys for specific features:
  - Fashn API credentials (for Virtual Try-On)
  - Database access (for NL2SQL)
---
## 🛠️ Troubleshooting

- SSL errors:  
  ```sh
  pip install --upgrade certifi
  export SSL_CERT_FILE=$(python -c "import certifi; print(certifi.where())")
  ```

---
## 📄 License

MIT License
