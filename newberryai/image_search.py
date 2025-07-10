import os
import json
import boto3
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv
import gradio as gr
from twelvelabs import TwelveLabs
import numpy as np

# Load environment variables
load_dotenv()

def extract_color_from_query(query):
    colors = ["red", "blue", "green", "yellow", "black", "white", "orange", "purple", "pink", "brown", "gray"]
    for color in colors:
        if color in query.lower():
            return color
    return None

def is_mostly_color(image, color, threshold=0.4):  # Try 0.4 or 0.5
    arr = np.array(image)
    if color == "red":
        mask = (arr[:,:,0] > 150) & (arr[:,:,1] < 100) & (arr[:,:,2] < 100)
    elif color == "blue":
        mask = (arr[:,:,2] > 150) & (arr[:,:,0] < 100) & (arr[:,:,1] < 100)
    elif color == "green":
        mask = (arr[:,:,1] > 150) & (arr[:,:,0] < 100) & (arr[:,:,2] < 100)
    elif color == "black":
        mask = (arr.mean(axis=2) < 50)
    elif color == "white":
        mask = (arr.mean(axis=2) > 200)
    # Add more colors as needed
    else:
        return True  # If color not handled, don't filter
    ratio = np.sum(mask) / (arr.shape[0] * arr.shape[1])
    return ratio > threshold

# --- S3 Utilities ---
class S3Utils:
    def __init__(self):
        self.s3 = boto3.client('s3')

    def upload_file(self, local_path, bucket, key):
        self.s3.upload_file(local_path, bucket, key)

    def download_file(self, bucket, key, local_path):
        self.s3.download_file(bucket, key, local_path)

    def get_image_keys_with_folders(self, bucket, prefix=""):
        image_info_list = []
        paginator = self.s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
        for page in pages:
            if "Contents" in page:
                for obj in page['Contents']:
                    key = obj['Key']
                    if key.endswith('/'):
                        continue
                    if key.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
                        parts = key[len(prefix):].split('/')
                        folder_name = parts[0] if len(parts) > 1 else "root"
                        image_info_list.append({
                            's3_path': f"s3://{bucket}/{key}",
                            'folder_name': folder_name,
                            's3_url': f"https://{bucket}.s3.amazonaws.com/{key}"
                        })
        return image_info_list

    def load_image_from_s3_path(self, s3_path):
        bucket, key = s3_path.replace("s3://", "").split("/", 1)
        obj = self.s3.get_object(Bucket=bucket, Key=key)
        return Image.open(obj['Body']).convert("RGB")

    def get_image_url_from_s3_path(self, s3_path, expires_in=3600, public=True):
        bucket, key = s3_path.replace("s3://", "").split("/", 1)
        if public:
            return f"https://{bucket}.s3.amazonaws.com/{key}"
        else:
            return self.s3.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': key}, ExpiresIn=expires_in)

# --- TwelveLabs Image Search ---
class ImageSearch:
    def __init__(self, s3_bucket, index_name="image-search-index"):
        self.s3_bucket = s3_bucket
        self.index_name = index_name
        self.s3_utils = S3Utils()
        self.tl_api_key = os.getenv("TWELVE_LABS_API_KEY") or os.getenv("TL_API_KEY")
        if not self.tl_api_key:
            raise ValueError("TwelveLabs API key not found in environment variables.")
        self.tl_client = TwelveLabs(api_key=self.tl_api_key)
        self.index_id = None
        self._ensure_index()

    def _ensure_index(self):
        # Check if index exists, else create
        indexes = self.tl_client.index.list()
        for idx in indexes:
            if idx.name == self.index_name:
                self.index_id = idx.id
                break
        if not self.index_id:
            idx = self.tl_client.index.create(
                name=self.index_name,
                models=[{"name": "marengo2.7", "options": ["visual"]}]
            )
            self.index_id = idx.id

    def build_index(self, prefix=""):
        print(f"Building index from images in S3 bucket: {self.s3_bucket}, prefix: '{prefix}'")
        image_info_list = self.s3_utils.get_image_keys_with_folders(self.s3_bucket, prefix)
        # Upload images to TwelveLabs index
        for img in image_info_list:
            s3_url = img['s3_url']
            try:
                self.tl_client.task.create(index_id=self.index_id, file=s3_url, language="en")
            except Exception as e:
                print(f"Error uploading {s3_url} to TwelveLabs: {e}")
        print("Index build tasks submitted. Wait for indexing to complete in the TwelveLabs dashboard.")

    def search(self, text_query, k=5, folder=None):
        options = ["visual"]
        results = self.tl_client.search.query(
            index_id=self.index_id,
            query_text=text_query,
            options=options
        )
        color = extract_color_from_query(text_query)
        filtered = []
        count = 0
        for clip in results.data:
            s3_url = getattr(clip, 'file_url', None) or getattr(clip, 'url', None) or None
            folder_name = None
            if s3_url:
                for img in self.s3_utils.get_image_keys_with_folders(self.s3_bucket):
                    if img['s3_url'] == s3_url:
                        folder_name = img['folder_name']
                        break
            # Color filtering
            if color and s3_url:
                try:
                    pil_img = self.s3_utils.load_image_from_s3_path(s3_url.replace("https://", "s3://").replace(".s3.amazonaws.com/", "/"))
                    if not is_mostly_color(pil_img, color, threshold=0.4):
                        continue
                except Exception as e:
                    pass  # If image can't be loaded, skip color filtering
            if folder is None or (folder_name and folder_name.lower() == folder.lower()):
                filtered.append({
                    "score": getattr(clip, 'score', None),
                    "s3_url": s3_url,
                    "folder": folder_name,
                    "start": getattr(clip, 'start', None),
                    "end": getattr(clip, 'end', None)
                })
                count += 1
            if count >= k:
                break
        return filtered

    def get_folders(self):
        image_info_list = self.s3_utils.get_image_keys_with_folders(self.s3_bucket)
        return list(sorted(set(img['folder_name'] for img in image_info_list)))

    # --- Gradio UI ---
    def start_gradio(self):
        def search_interface(text_query, k, folder):
            results = self.search(text_query, k=k, folder=folder if folder != "All" else None)
            return [r["s3_url"] for r in results if r["s3_url"]]
        folder_choices = ["All"] + self.get_folders()
        interface = gr.Interface(
            fn=search_interface,
            inputs=[
                gr.Textbox(label="Text Query", placeholder="Describe the image you want..."),
                gr.Slider(minimum=1, maximum=10, value=5, step=1, label="Top K Results"),
                gr.Dropdown(choices=folder_choices, value="All", label="Folder (optional)")
            ],
            outputs=gr.Gallery(label="Search Results"),
            title="Image Search (S3 + TwelveLabs)",
            description="Search your S3 image collection using natural language via TwelveLabs."
        )
        return interface.launch(share=True)

    # --- CLI ---
    def run_cli(self):
        print("Image Search CLI initialized.")
        print("Type 'exit' or 'quit' to end.")
        while True:
            text = input("\nEnter your search query: ")
            if text.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            k = input("How many results? (default 5): ")
            k = int(k) if k.strip().isdigit() else 5
            folder = input("Filter by folder (leave blank for all): ")
            folder = folder.strip() or None
            try:
                results = self.search(text, k=k, folder=folder)
                print("\nResults:")
                for r in results:
                    print(f"{r['s3_url']} (score: {r['score']}, folder: {r['folder']})")
            except Exception as e:
                print(f"Error: {str(e)}")

# --- CLI/Gradio Entrypoint ---
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Image Search System (S3 + TwelveLabs)")
    parser.add_argument('--s3_bucket', required=True, help='S3 bucket name')
    parser.add_argument('--build_index', action='store_true', help='Build index from S3 images')
    parser.add_argument('--prefix', default='', help='S3 prefix/folder (optional)')
    parser.add_argument('--gradio', action='store_true', help='Launch Gradio UI')
    parser.add_argument('--cli', action='store_true', help='Run CLI')
    args = parser.parse_args()
    searcher = ImageSearch(s3_bucket=args.s3_bucket)
    if args.build_index:
        searcher.build_index(prefix=args.prefix)
    elif args.gradio:
        searcher.start_gradio()
    elif args.cli:
        searcher.run_cli()
    else:
        print("No action specified. Use --build_index, --gradio, or --cli.")
