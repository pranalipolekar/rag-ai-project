import os
import requests
import numpy as np
import faiss
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
from typing import List, Dict
import uvicorn
import yaml


# =============================
# CONFIG
# =============================

# Load YAML file
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# Access values
ENVIRONMENT = config.get("ENVIRONMENT", "dev")
OPENAI_API_KEY = config.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in config.yaml")

# Set OpenAI key
openai.api_key = OPENAI_API_KEY

START_URL = "https://www.w3schools.com/python/"
MAX_PAGES = 15
CHUNK_SIZE = 400
CHUNK_OVERLAP = 100

# =============================
# 1. CRAWL WEBSITE (FIXED)
# =============================

def crawl_w3schools(start_url, max_pages):
    """
    Fixed version with proper page limit checking and metadata preservation
    """
    visited = set()
    pages = []

    def crawl(url):
        # FIX: Check pages length, not visited length
        if url in visited or len(pages) >= max_pages:
            return

        print(f"Crawling: {url} ({len(pages) + 1}/{max_pages})")
        visited.add(url)

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # FIX: Check for HTTP errors
            soup = BeautifulSoup(response.text, "html.parser")

            # Remove scripts, styles, nav
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()

            text = soup.get_text(separator=" ", strip=True)
            
            # FIX: Only add pages with substantial content
            if len(text) > 100:
                # FIX: Add title for better source attribution
                title = soup.find("title")
                title = title.get_text() if title else url
                
                pages.append({
                    "url": url,
                    "title": title,
                    "text": text
                })

            # Only continue crawling if we haven't hit the limit
            if len(pages) < max_pages:
                for link in soup.find_all("a", href=True):
                    next_url = urljoin(url, link["href"])
                    # Remove URL fragments
                    next_url = next_url.split('#')[0]
                    
                    if (
                        urlparse(next_url).netloc == "www.w3schools.com"
                        and next_url.startswith(start_url)
                        and next_url not in visited
                    ):
                        crawl(next_url)

        except Exception as e:
            print(f"Failed to crawl {url}: {e}")

    crawl(start_url)
    return pages

# =============================
# 2. CHUNK TEXT (FIXED)
# =============================

def chunk_text(text, size, overlap):
    """
    Chunk text with word-based splitting
    """
    words = text.split()
    chunks = []

    for i in range(0, len(words), size - overlap):
        chunk = " ".join(words[i:i + size])
        # Only keep chunks with meaningful content
        if len(chunk.strip()) > 50:
            chunks.append(chunk)

    return chunks

# =============================
# 3. EMBEDDINGS
# =============================

def get_embedding(text):
    """
    Get embedding from OpenAI
    """
    try:
        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {e}")
        raise

# =============================
# 4. VECTOR STORE (FIXED)
# =============================

class VectorStore:
    """
    Fixed version with metadata tracking
    """
    def __init__(self, dim):
        self.index = faiss.IndexFlatL2(dim)
        self.texts = []
        self.metadata = []  # FIX: Track metadata (URL, title)

    def add(self, embedding, text, metadata=None):
        """
        Add vector with metadata
        """
        vector = np.array([embedding]).astype("float32")
        self.index.add(vector)
        self.texts.append(text)
        self.metadata.append(metadata or {})  # FIX: Store metadata

    def search(self, embedding, k=3):
        """
        Search and return texts with metadata
        """
        vector = np.array([embedding]).astype("float32")
        distances, indices = self.index.search(vector, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.texts):  # Sanity check
                results.append({
                    'text': self.texts[idx],
                    'metadata': self.metadata[idx],
                    'distance': float(distances[0][i])
                })
        
        return results

# =============================
# 5. BUILD VECTOR STORE (FIXED)
# =============================

def build_store(pages):
    """
    Fixed version with metadata preservation
    """
    store = None
    total_chunks = 0

    for page in pages:
        chunks = chunk_text(page["text"], CHUNK_SIZE, CHUNK_OVERLAP)
        
        for chunk_id, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)
            
            if store is None:
                store = VectorStore(len(embedding))
            
            # FIX: Add metadata for source attribution
            metadata = {
                'url': page['url'],
                'title': page['title'],
                'chunk_id': chunk_id
            }
            
            store.add(embedding, chunk, metadata)
            total_chunks += 1
            
            if total_chunks % 10 == 0:
                print(f"  Processed {total_chunks} chunks...")

    print(f"  Total chunks: {total_chunks}")
    return store

# =============================
# 6. ANSWER QUESTION (FIXED)
# =============================

def answer_question(store, question):
    """
    Fixed version with error handling and source attribution
    """
    try:
        # Get query embedding
        query_embedding = get_embedding(question)
        
        # Search for relevant chunks
        results = store.search(query_embedding, k=3)
        
        if not results:
            return {
                "answer": "I don't have enough information to answer this question.",
                "sources": []
            }
        
        # Build context from results
        context_parts = []
        sources = []
        
        for result in results:
            context_parts.append(result['text'])
            sources.append({
                'url': result['metadata'].get('url', 'Unknown'),
                'title': result['metadata'].get('title', 'Unknown'),
                'relevance': 1 / (1 + result['distance'])  # Convert distance to relevance
            })
        
        context = "\n\n".join(context_parts)

        # FIX: Better prompt with stricter instructions
        prompt = f"""You are a W3Schools support bot.
Answer the question using ONLY the context provided below.

RULES:
- If the answer is not in the context, say "I don't have enough information to answer this question."
- Be concise and accurate
- Do not make up information
- Base your answer solely on the provided context

Context:
{context}

Question: {question}

Answer:"""

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0  # FIX: Use temperature=0 for more consistent answers
        )

        return {
            "answer": response.choices[0].message.content,
            "sources": sources
        }
    
    except Exception as e:
        print(f"Error answering question: {e}")
        raise

# =============================
# 7. FASTAPI APP (FIXED)
# =============================

app = FastAPI(title="RAG Q&A Support Bot")

class Question(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str
    sources: List[Dict]

# Global store
vector_store = None

@app.on_event("startup")
async def startup_event():
    """
    FIX: Initialize on startup with error handling
    """
    global vector_store
    
    try:
        print("="*60)
        print("Starting crawl...")
        pages = crawl_w3schools(START_URL, MAX_PAGES)
        print(f"✓ Crawled {len(pages)} pages")
        
        print("\nBuilding vector store...")
        vector_store = build_store(pages)
        print("✓ Vector store ready")
        print("="*60)
        
    except Exception as e:
        print(f"ERROR during startup: {e}")
        raise

@app.get("/")
def root():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "message": "RAG Q&A Bot is running",
        "chunks": len(vector_store.texts) if vector_store else 0
    }

@app.post("/ask", response_model=AnswerResponse)
def ask(question: Question):
    """
    FIX: Added error handling
    """
    try:
        if vector_store is None:
            raise HTTPException(
                status_code=503,
                detail="Vector store not initialized yet"
            )
        
        result = answer_question(vector_store, question.question)
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )

@app.get("/stats")
def stats():
    """
    NEW: Get statistics about the knowledge base
    """
    if vector_store is None:
        raise HTTPException(
            status_code=503,
            detail="Vector store not initialized yet"
        )
    
    unique_urls = set()
    for metadata in vector_store.metadata:
        unique_urls.add(metadata.get('url', 'Unknown'))
    
    return {
        "total_chunks": len(vector_store.texts),
        "total_pages": len(unique_urls),
        "embedding_dimension": vector_store.index.d
    }

# =============================
# MAIN
# =============================

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)