# NewberryAI

**AI-powered toolkit for healthcare, compliance, document analysis, and more.**

---

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
- **PDF Extractor**: Extract and query content from PDF documents using embeddings and semantic search
- **Video Generator**: Generate videos from text using Amazon Bedrock's Nova model
- **Image Generator**: Generate images from text using Amazon Bedrock's Titan Image Generator
- **Face Recognition**: Add and recognize faces using AWS Rekognition
- **Face Detection**: Process videos and detect faces using AWS Rekognition
- **Natural Language to SQL (NL2SQL) Assistant**: Generate SQL queries from natural language
- **Virtual Try-On**: Generate virtual try-on images using AI



## 🛠️ Installation

```sh
pip install newberryai
```

## 📚 Feature Usage

### 1. Compliance Checker

#### Python SDK

```python
from newberryai import ComplianceChecker
checker = ComplianceChecker()
result, status_code = checker.check_compliance("video.mp4", "Is the video compliant with safety regulations?")
print(f'Compliant: {"Yes" if result["compliant"] else "No"}')
print(f'Analysis: {result["analysis"]}')
```

#### CLI

```sh
newberryai compliance --video_file path/to/video.mp4 --question "Is the video compliant with safety regulations?"
```

#### Gradio

```sh
newberryai compliance --gradio
```

---

### 2. HealthScribe

#### Python SDK

```python
from newberryai import HealthScribe
scribe = HealthScribe(
    input_s3_bucket="your-bucket",
    data_access_role_arn="arn:aws:iam::account:role/your-role"
)
result = scribe.process(
    file_path="audio.wav",
    job_name="job1",
    output_s3_bucket="your-bucket"
)
print(result["summary"])
```

#### CLI

```sh
newberryai healthscribe --file_path audio.wav --job_name job1 --data_access_role_arn arn:aws:iam::account:role/your-role --input_s3_bucket your-bucket --output_s3_bucket your-bucket
```

---

### 3. Differential Diagnosis

#### Python SDK

```python
from newberryai import DDxChat
ddx = DDxChat()
response = ddx.ask("Patient presents with fever, cough, and fatigue for 5 days")
print(response)
```

#### CLI

```sh
newberryai ddx --clinical_indication "Patient presents with fever, cough, and fatigue for 5 days"
newberryai ddx --interactive
newberryai ddx --gradio
```

---

### 4. Excel Formula Generator

#### Python SDK

```python
from newberryai import ExcelExp
excel = ExcelExp()
response = excel.ask("Give me an Excel formula to calculate average sales for 2010 and 2011")
print(response)
```

#### CLI

```sh
newberryai ExcelO --Excel_query "Give me an Excel formula to calculate average sales for 2010 and 2011"
newberryai ExcelO --interactive
newberryai ExcelO --gradio
```

---

### 5. Medical Bill Extractor

#### Python SDK

```python
from newberryai import Bill_extractor
extractor = Bill_extractor()
analysis = extractor.analyze_document("medical_bill.jpg")
print(analysis)
```

#### CLI

```sh
newberryai bill_extract --file_path medical_bill.jpg
newberryai bill_extract --interactive
newberryai bill_extract --gradio
```

---

### 6. Coding Assistant

#### Python SDK

```python
from newberryai import CodeReviewAssistant
debugger = CodeReviewAssistant()
response = debugger.ask("Explain and correct this code: ...")
print(response)
```

#### CLI

```sh
newberryai Coder --code_query "Explain and correct this code: ..."
newberryai Coder --interactive
newberryai Coder --gradio
```

---

### 7. PII Redactor

#### Python SDK

```python
from newberryai import PII_Redaction
pii_red = PII_Redaction()
response = pii_red.ask("Patient name is John Doe with fever. Email: john.doe@email.com")
print(response)
```

#### CLI

```sh
newberryai PII_Red --text "Patient name is John Doe with fever. Email: john.doe@email.com"
newberryai PII_Red --interactive
newberryai PII_Red --gradio
```

---

### 8. PII Extractor

#### Python SDK

```python
from newberryai import PII_extraction
pii_extract = PII_extraction()
response = pii_extract.ask("Patient name is John Doe with fever. Email: john.doe@email.com")
print(response)
```

#### CLI

```sh
newberryai PII_extract --text "Patient name is John Doe with fever. Email: john.doe@email.com"
newberryai PII_extract --interactive
newberryai PII_extract --gradio
```

---

### 9. EDA Assistant

#### Python SDK

```python
from newberryai import EDA
import pandas as pd
eda = EDA()
eda.current_data = pd.read_csv("data.csv")
response = eda.ask("What is the average value of column 'Sales'?")
print(response)

# Visualizations
eda.visualize_data('dist')
eda.visualize_data('corr')
eda.visualize_data('cat')
eda.visualize_data('time')
```

#### CLI

```sh
newberryai eda --file_path data.csv --interactive
newberryai eda --file_path data.csv --gradio
```

---

### 10. PDF Summarizer

#### Python SDK

```python
from newberryai import DocSummarizer
summarizer = DocSummarizer()
response = summarizer.ask("document.pdf")
print(response)
```

#### CLI

```sh
newberryai pdf_summarizer --file_path document.pdf
newberryai pdf_summarizer --interactive
newberryai pdf_summarizer --gradio
```

---

### 11. PDF Extractor

#### Python SDK

```python
import asyncio
from newberryai import PDFExtractor
async def extract():
    extractor = PDFExtractor()
    pdf_id = await extractor.process_pdf("document.pdf")
    response = await extractor.ask_question(pdf_id, "What is the main point?")
    print(response["answer"])
asyncio.run(extract())
```

#### CLI

```sh
newberryai pdf_extract --file_path document.pdf --question "What is the main point?"
newberryai pdf_extract --interactive
newberryai pdf_extract --gradio
```

---

### 12. Video Generator

#### Python SDK

```python
from newberryai import VideoGenerator
generator = VideoGenerator()
async def run_video():
    response = await generator.generate(
        text= "A cat dancing on a wall",
        duration_seconds=6, #Optional
        fps=24, #Optional
        dimension="1280x720", #Optional
        seed=42 #Optional
    )
    print(response["message"])
    print("Waiting for video to complete...")
    final_response = await generator.wait_for_completion(response["job_id"])
    print(final_response["message"])
    print(f"Video URL: {final_response['video_url']}")
await run_video()
```

#### CLI

```sh
newberryai video --text "A beautiful sunset over the ocean" --duration 10 --fps 30 --dimension 1920x1080 --output video.mp4
newberryai video --interactive
newberryai video --gradio
```

---

### 13. Image Generator

#### Python SDK

```python
from newberryai.image_generator import ImageGenerator
generator = ImageGenerator()
result = await generator.generate(
    text= "A lotus in a muddy pond",
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

#### CLI

```sh
newberryai image --text "A lotus in a muddy pond" --width 512 --height 512 --number_of_images 1 --quality standard
newberryai image --interactive
newberryai image --gradio
```

---

### 14. Face Recognition

#### Python SDK

```python
from newberryai import FaceRecognition, FaceRequest
from newberryai.face_recognigation import FaceRequest #Alternative
face_recognition = FaceRecognition()
add_response = face_recognition.add_to_collect(FaceRequest(image_path="face.jpg", name="Name"))
print(add_response.message)
if add_response.success:
    print(f"Face ID: {add_response.face_id}")

recognize_response = face_recognition.recognize_image(
    FaceRequest(image_path="vishnu2.jpg")
)
print(recognize_response.message)
if recognize_response.success:
    print(f"Recognized: {recognize_response.name} (Confidence: {recognize_response.confidence:.2f}%)")

```

#### CLI

```sh
newberryai face_recognig --image_path face.jpg --add --name "Name"
newberryai face_recognig --interactive
newberryai face_recognig --gradio
```

---

### 15. Face Detection

#### Python SDK

```python
from newberryai import FaceDetection
from newberryai.face_detection import VideoRequest
face_detector = FaceDetection()
response = face_detector.add_face_to_collection("face.jpg", "Name")
results = face_detector.process_video(VideoRequest(video_path="video.mp4", max_frames=20))
```

#### CLI

```sh
newberryai face_detect --add_image face.jpg --name "Name"
newberryai face_detect --video_path video.mp4 --max_frames 20
newberryai face_detect --interactive
newberryai face_detect --gradio
```

---

### 16. NL2SQL Assistant

#### Python SDK

```python
from newberryai import NL2SQL, DatabaseConfig, NL2SQLRequest
nl2sql = NL2SQL()
db_config = DatabaseConfig(host="localhost", user="root", password="pass", database="db")
nl2sql.connect_to_database(db_config)
request = NL2SQLRequest(question="Show tables")
response = nl2sql.process_query(request)
print(response.generated_sql)
```

#### CLI

```sh
newberryai nl2sql --question "Show tables" --user root --password pass --database db
newberryai nl2sql --interactive
newberryai nl2sql --gradio
```

---

### 17. Virtual Try-On

#### Python SDK

```python
from newberryai import VirtualTryOn

try_on = VirtualTryOn()

request = await try_on.process(
    model_image='vishnu.jpg',
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

#### CLI

```sh
newberryai tryon --model_image model.jpg --garment_image garment.jpg --category tops
newberryai tryon --interactive
newberryai tryon --gradio
```

---

## ⚙️ Requirements & Setup

- Python 3.8+
- AWS credentials (for AWS-powered features)
- OpenAI API key (for LLM features)
- Fashn API credentials (for Virtual Try-On)
- See [docs](#) for environment variable setup.

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

---

**For more details, see the [full documentation](https://github.com/HolboxAI/newberryai).**

This project is licensed under the MIT License.
