import os
import time
import asyncio
import uuid
import numpy as np
import fitz  # PyMuPDF
import openai
import faiss
import gradio as gr
from typing import List, Dict, Optional
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Configuration
BASE_DIR = Path(__file__).parent.parent
TEMP_UPLOAD_DIR = BASE_DIR / "tmp_uploads"
TEMP_UPLOAD_DIR.mkdir(exist_ok=True)

PDF_TTL_SECONDS = 3600  # 1 hour TTL
CLEANUP_INTERVAL_SECONDS = 1800  # Cleanup every 30 mins
EMBED_DIM = 1536  # OpenAI's text-embedding-ada-002 dimension

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OpenAI API key not found. Please set it in the .env file.")

# Initialize FAISS
index = faiss.IndexFlatIP(EMBED_DIM)
metadata_store = {}
vector_id_counter = 0

class PDFExtractor:
    def __init__(self):
        self.cleanup_task = None
        self.current_pdf_id = None

    async def start_cleanup_task(self):
        """Start the background cleanup task."""
        if self.cleanup_task is None:
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def _cleanup_loop(self):
        """Background task to clean up old PDFs and their vectors."""
        while True:
            now = time.time()
            deleted_files = []
            for filepath in TEMP_UPLOAD_DIR.glob("*.pdf"):
                if not filepath.is_file():
                    continue
                file_age = now - filepath.stat().st_mtime
                if file_age > PDF_TTL_SECONDS:
                    try:
                        filepath.unlink()
                        self.delete_vectors_by_pdf_id(filepath.name)
                        deleted_files.append(filepath.name)
                    except Exception as e:
                        print(f"Failed to delete {filepath.name}: {e}")
            if deleted_files:
                print(f"Cleanup: Removed PDFs and vectors for {deleted_files}")
            await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)

    def extract_text_from_pdf(self, pdf_path: str) -> List[str]:
        """Extract text from PDF pages."""
        doc = fitz.open(pdf_path)
        pages = []
        for page in doc:
            pages.append(page.get_text())
        return pages

    def chunk_text(self, pages: List[str], max_chunk_size: int = 500) -> List[str]:
        """Split text into chunks of specified size."""
        chunks = []
        for page_text in pages:
            words = page_text.split()
            for i in range(0, len(words), max_chunk_size):
                chunk = " ".join(words[i:i+max_chunk_size])
                chunks.append(chunk)
        return chunks

    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding using OpenAI API."""
        response = openai.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        vector = np.array(response.data[0].embedding, dtype=np.float32)
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector /= norm
        return vector

    def store_embeddings(self, pdf_id: str, chunks: List[str]) -> List[str]:
        """Store embeddings in FAISS index."""
        global vector_id_counter
        chunk_ids = []
        vectors = []
        ids = []

        for idx, chunk in enumerate(chunks):
            chunk_id = str(uuid.uuid4())
            vector = self.embed_text(chunk)
            vectors.append(vector)
            ids.append(vector_id_counter)

            metadata_store[vector_id_counter] = {
                "chunk_id": chunk_id,
                "pdf_id": pdf_id,
                "chunk_index": idx,
                "text": chunk,
            }
            chunk_ids.append(chunk_id)
            vector_id_counter += 1

        if vectors:
            vectors_np = np.vstack(vectors)
            index.add(vectors_np)

        return chunk_ids

    def query_embeddings(self, pdf_id: str, query_text: str, top_k: int = 3) -> List[Dict]:
        """Query similar chunks from the given PDF."""
        if index.ntotal == 0:
            return []

        query_vector = self.embed_text(query_text).reshape(1, -1)
        D, I = index.search(query_vector, top_k * 5)

        results = []
        for idx in I[0]:
            if idx == -1:
                continue
            meta = metadata_store.get(idx)
            if meta and meta['pdf_id'] == pdf_id:
                results.append(meta)
                if len(results) >= top_k:
                    break

        return results

    def generate_answer(self, question: str, context_chunks: List[str]) -> str:
        """Generate answer using GPT-4."""
        system_prompt = "You are an AI assistant helping to answer questions based on the provided document excerpts."
        context_text = "\n\n---\n\n".join(context_chunks)
        user_prompt = (
            f"Use the following excerpts from a document to answer the question.\n\n"
            f"Context:\n{context_text}\n\n"
            f"Question: {question}\n\n"
            f"Answer:"
        )

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=500,
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()

    def delete_vectors_by_pdf_id(self, pdf_id: str):
        """Delete vectors and metadata for a given PDF."""
        global index, metadata_store, vector_id_counter

        keep_ids = [vid for vid, meta in metadata_store.items() if meta['pdf_id'] != pdf_id]
        new_metadata_store = {vid: metadata_store[vid] for vid in keep_ids}

        vectors_to_keep = []
        id_mapping = {}
        for new_id, old_id in enumerate(keep_ids):
            id_mapping[old_id] = new_id
            vectors_to_keep.append(index.reconstruct(old_id))

        index = faiss.IndexFlatIP(EMBED_DIM)
        if vectors_to_keep:
            index.add(np.vstack(vectors_to_keep).astype(np.float32))

        metadata_store = new_metadata_store
        vector_id_counter = len(metadata_store)

    async def process_pdf(self, pdf_path: str) -> str:
        """Process a PDF file and store its embeddings."""
        pdf_id = Path(pdf_path).name
        pages = self.extract_text_from_pdf(pdf_path)
        chunks = self.chunk_text(pages)
        self.store_embeddings(pdf_id, chunks)
        return pdf_id

    async def ask_question(self, pdf_id: str, question: str) -> Dict[str, str]:
        """Ask a question about a specific PDF."""
        results = self.query_embeddings(pdf_id, question)
        context_chunks = [r["text"] for r in results]
        answer = self.generate_answer(question, context_chunks)
        return {
            "answer": answer,
            "source_chunks": context_chunks
        }

    def start_gradio(self):
        """Launch the Gradio web interface."""
        def process_pdf_and_ask(pdf_file, question):
            if pdf_file is None:
                return "Please upload a PDF file first."
            
            # Process PDF
            pdf_id = asyncio.run(self.process_pdf(pdf_file.name))
            self.current_pdf_id = pdf_id
            
            if not question:
                return "PDF processed successfully. You can now ask questions about it."
            
            # Ask question
            response = asyncio.run(self.ask_question(pdf_id, question))
            return response["answer"]

        # Create Gradio interface
        iface = gr.Interface(
            fn=process_pdf_and_ask,
            inputs=[
                gr.File(label="Upload PDF"),
                gr.Textbox(label="Question about the PDF")
            ],
            outputs=[
                gr.Textbox(label="Answer")
            ],
            title="PDF Question Answering",
            description="Upload a PDF and ask questions about its content."
        )
        
        iface.launch(share=True, server_name="0.0.0.0")

    def run_cli(self):
        """Run the interactive CLI interface."""
        print("PDF Question Answering CLI")
        print("-------------------------")
        
        while True:
            # Get PDF file
            pdf_path = input("\nEnter path to PDF file (or 'q' to quit): ").strip()
            if pdf_path.lower() == 'q':
                break
                
            if not os.path.exists(pdf_path):
                print(f"Error: File not found at {pdf_path}")
                continue
                
            try:
                # Process PDF
                print("Processing PDF...")
                pdf_id = asyncio.run(self.process_pdf(pdf_path))
                self.current_pdf_id = pdf_id
                print("PDF processed successfully!")
                
                # Interactive Q&A
                while True:
                    question = input("\nEnter your question (or 'q' to quit, 'new' for new PDF): ").strip()
                    if question.lower() == 'q':
                        return
                    if question.lower() == 'new':
                        break
                        
                    if not question:
                        continue
                        
                    print("\nGenerating answer...")
                    response = asyncio.run(self.ask_question(pdf_id, question))
                    
                    print("\nAnswer:")
                    print(response["answer"])
                    print("\nSource Chunks:")
                    for chunk in response["source_chunks"]:
                        print(f"\n---\n{chunk}")
                        
            except Exception as e:
                print(f"Error: {str(e)}")
                continue
