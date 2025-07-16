import os
import json
import boto3
import faiss
import numpy as np
import base64
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv
import gradio as gr

# Load environment variables
load_dotenv()

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
                            'folder_name': folder_name
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

# --- Embedder (Amazon Titan Multimodal Embeddings G1) ---
class Embedder:
    def __init__(self, embedding_length=1024, region_name=None):
        self.bedrock = boto3.client('bedrock-runtime', region_name=region_name)
        self.model_id = "amazon.titan-embed-image-v1"
        self.embedding_length = embedding_length

    def _encode_image_to_base64(self, image: Image.Image):
        from io import BytesIO
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def get_image_embeddings(self, image_info_list, s3_utils):
        embeddings = []
        processed_image_info = []
        for img_info in image_info_list:
            s3_path = img_info['s3_path']
            try:
                image = s3_utils.load_image_from_s3_path(s3_path)
                image_string = self._encode_image_to_base64(image)
                body = json.dumps({
                    "inputImage": image_string,
                    "embeddingConfig": {"outputEmbeddingLength": self.embedding_length}
                })
                response = self.bedrock.invoke_model(
                    modelId=self.model_id,
                    body=body,
                    accept="application/json",
                    contentType="application/json"
                )
                response_body = json.loads(response['body'].read())
                embedding = np.array(response_body['embedding']).reshape(1, -1)
                embeddings.append(embedding)
                processed_image_info.append(img_info)
            except Exception as e:
                print(f"Error processing image {s3_path}: {e}. Skipping.")
                continue
        if not embeddings:
            return np.array([]), []
        return np.vstack(embeddings), processed_image_info

    def get_text_embedding(self, text_query):
        body = json.dumps({
            "inputText": text_query,
            "embeddingConfig": {"outputEmbeddingLength": self.embedding_length}
        })
        response = self.bedrock.invoke_model(
            modelId=self.model_id,
            body=body,
            accept="application/json",
            contentType="application/json"
        )
        response_body = json.loads(response['body'].read())
        return np.array(response_body['embedding']).reshape(1, -1)

    def get_image_embedding_from_pil(self, image):
        image_string = self._encode_image_to_base64(image)
        body = json.dumps({
            "inputImage": image_string,
            "embeddingConfig": {"outputEmbeddingLength": self.embedding_length}
        })
        response = self.bedrock.invoke_model(
            modelId=self.model_id,
            body=body,
            accept="application/json",
            contentType="application/json"
        )
        response_body = json.loads(response['body'].read())
        return np.array(response_body['embedding']).reshape(1, -1)

# --- VectorStore (FAISS) ---
class VectorStore:
    def __init__(self):
        self.index = None
        self.metadata = None

    def build_and_save_index(self, embeddings, image_info, index_file, metadata_file, s3_utils, s3_bucket):
        if embeddings.shape[0] == 0:
            print("No embeddings to build index. Exiting.")
            return
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)
        faiss.write_index(self.index, index_file)
        image_metadata = {str(i): {'s3_path': info['s3_path'], 'folder_name': info['folder_name']} for i, info in enumerate(image_info)}
        with open(metadata_file, 'w') as f:
            json.dump(image_metadata, f, indent=4)
        s3_utils.upload_file(index_file, s3_bucket, index_file)
        s3_utils.upload_file(metadata_file, s3_bucket, metadata_file)

    def load_index_and_metadata(self, index_file, metadata_file):
        self.index = faiss.read_index(index_file)
        with open(metadata_file, 'r') as f:
            self.metadata = json.load(f)

    def search_images(self, query_embedding, k=5, filter_folder=None):
        query_embedding = query_embedding.reshape(1, -1)
        distances, indices = self.index.search(query_embedding, self.index.ntotal)
        results = []
        sorted_results = sorted([(distances[0][i], idx) for i, idx in enumerate(indices[0]) if idx != -1])
        count = 0
        for distance, idx in sorted_results:
            if count >= k:
                break
            metadata_entry = self.metadata[str(idx)]
            s3_path = metadata_entry['s3_path']
            folder_name = metadata_entry['folder_name']
            if filter_folder is None or folder_name.lower() == filter_folder.lower():
                results.append((distance, s3_path, folder_name))
                count += 1
        return results

    def get_unique_folder_names(self):
        unique_folders = set()
        for item_id, item_data in self.metadata.items():
            if 'folder_name' in item_data:
                unique_folders.add(item_data['folder_name'].lower())
        return list(unique_folders)

# --- Main ImageSearch Class ---
class ImageSearch:
    def __init__(self, s3_bucket, index_file="faiss.index", metadata_file="metadata.json", embedding_length=1024, region_name=None):
        self.s3_bucket = s3_bucket
        self.index_file = index_file
        self.metadata_file = metadata_file
        self.s3_utils = S3Utils()
        self.embedder = Embedder(embedding_length=embedding_length, region_name=region_name)
        self.vectorstore = VectorStore()
        self.index_loaded = False

    def build_index(self, prefix=""):
        print(f"Building index from images in S3 bucket: {self.s3_bucket}, prefix: '{prefix}'")
        image_info_list = self.s3_utils.get_image_keys_with_folders(self.s3_bucket, prefix)
        embeddings, processed_image_info = self.embedder.get_image_embeddings(image_info_list, self.s3_utils)
        self.vectorstore.build_and_save_index(embeddings, processed_image_info, self.index_file, self.metadata_file, self.s3_utils, self.s3_bucket)
        print("Index built and saved.")

    def load_index(self):
        self.vectorstore.load_index_and_metadata(self.index_file, self.metadata_file)
        self.index_loaded = True

    def search(self, text_query, k=5, folder=None):
        if not self.index_loaded:
            self.load_index()
        query_embedding = self.embedder.get_text_embedding(text_query)
        results = self.vectorstore.search_images(query_embedding, k=k, filter_folder=folder)
        return [
            {
                "distance": float(distance),
                "s3_path": s3_path,
                "folder": folder_name,
                "image_url": self.s3_utils.get_image_url_from_s3_path(s3_path)
            }
            for distance, s3_path, folder_name in results
        ]

    def search_by_image(self, image, k=5, folder=None):
        if not self.index_loaded:
            self.load_index()
        query_embedding = self.embedder.get_image_embedding_from_pil(image)
        results = self.vectorstore.search_images(query_embedding, k=k, filter_folder=folder)
        return [
            {
                "distance": float(distance),
                "s3_path": s3_path,
                "folder": folder_name,
                "image_url": self.s3_utils.get_image_url_from_s3_path(s3_path)
            }
            for distance, s3_path, folder_name in results
        ]

    def get_folders(self):
        if not self.index_loaded:
            self.load_index()
        return self.vectorstore.get_unique_folder_names()

    # --- Gradio UI ---
    def start_gradio(self):
        def text_search_interface(text_query, k, folder):
            results = self.search(text_query, k=k, folder=folder if folder != "All" else None)
            return [r["image_url"] for r in results]
        def image_search_interface(image, k, folder):
            if image is None:
                return []
            pil_image = image if isinstance(image, Image.Image) else Image.open(image)
            results = self.search_by_image(pil_image, k=k, folder=folder if folder != "All" else None)
            return [r["image_url"] for r in results]
        folder_choices = ["All"] + self.get_folders()
        text_tab = gr.Interface(
            fn=text_search_interface,
            inputs=[
                gr.Textbox(label="Text Query", placeholder="Describe the image you want..."),
                gr.Slider(minimum=1, maximum=10, value=5, step=1, label="Top K Results"),
                gr.Dropdown(choices=folder_choices, value="All", label="Folder (optional)")
            ],
            outputs=gr.Gallery(label="Search Results"),
            title="Text to Image Search"
        )
        image_tab = gr.Interface(
            fn=image_search_interface,
            inputs=[
                gr.Image(type="pil", label="Query Image"),
                gr.Slider(minimum=1, maximum=10, value=5, step=1, label="Top K Results"),
                gr.Dropdown(choices=folder_choices, value="All", label="Folder (optional)")
            ],
            outputs=gr.Gallery(label="Search Results"),
            title="Image to Image Search"
        )
        tabs = gr.TabbedInterface([text_tab, image_tab], tab_names=["Text to Image", "Image to Image"])
        return tabs.launch(share=True)

    # --- CLI ---
    def run_cli(self):
        print("Image Search CLI initialized.")
        print("Type 'exit' or 'quit' to end.")
        while True:
            mode = input("\nChoose search mode: (1) Text, (2) Image, (exit/quit): ").strip().lower()
            if mode in ["exit", "quit"]:
                print("Goodbye!")
                break
            if mode == "1" or mode.startswith("text"):
                text = input("Enter your search query: ")
                k = input("How many results? (default 5): ")
                k = int(k) if k.strip().isdigit() else 5
                folder = input("Filter by folder (leave blank for all): ")
                folder = folder.strip() or None
                try:
                    results = self.search(text, k=k, folder=folder)
                    print("\nResults:")
                    for r in results:
                        print(f"{r['image_url']} (distance: {r['distance']:.4f}, folder: {r['folder']})")
                except Exception as e:
                    print(f"Error: {str(e)}")
            elif mode == "2" or mode.startswith("image"):
                image_path = input("Enter path to query image: ").strip()
                if not os.path.exists(image_path):
                    print(f"File not found: {image_path}")
                    continue
                try:
                    pil_image = Image.open(image_path).convert("RGB")
                    k = input("How many results? (default 5): ")
                    k = int(k) if k.strip().isdigit() else 5
                    folder = input("Filter by folder (leave blank for all): ")
                    folder = folder.strip() or None
                    results = self.search_by_image(pil_image, k=k, folder=folder)
                    print("\nResults:")
                    for r in results:
                        print(f"{r['image_url']} (distance: {r['distance']:.4f}, folder: {r['folder']})")
                except Exception as e:
                    print(f"Error: {str(e)}")
            else:
                print("Invalid mode. Please enter 1 for Text, 2 for Image, or exit/quit.")
