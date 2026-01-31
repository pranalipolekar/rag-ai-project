# rag-ai-project - RAG Q&A Support Bot

A **Retrival Augmented Generation (RAG)** application that scrapes web content, transforms it into embeddings with OpenAI, stores vectors in FAISS, and answers questions using only the ingested pages.
## 📁 Project Structure

```
rag-ai-project/ contains:
|--.github/ — CI and GitHub config
|--.venv/ — Python virtual environment
|--main.py — Application entry point
|--README.md — This document
|--requirements.txt — Dependency list
```




## 🎯 What This System Does

This RAG bot:
1. Crawl a target website (example: W3Schools Python tutorial)
2. Clean and extract meaningful text
3. Split text into chunks
4. Create embeddings via OpenAI
5. Persist vectors in a FAISS index
6. Retrieve relevant chunks for a query
7. Generate answers with GPT-4 constrained to retrieved content
8. Expose results through a FastAPI endpoint
           
```bash  
## 🚀 Quick Start
1. Clone the repository
git clone https://github.com/pranalipolekar/rag-ai-project.git
cd rag-ai-project
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set OpenAI API Key

```bash
# On Windows (Command Prompt):
set OPENAI_API_KEY=your-api-key-here

# On Windows (PowerShell):
$env:OPENAI_API_KEY="your-api-key-here"

# On macOS/Linux:
export OPENAI_API_KEY="your-api-key-here"
```

### 5. Run the Application

```bash
python main.py
```

The server will start on `http://localhost:8000`

## 📋 Dependencies

The `requirements.txt` file should contain:

```
fastapi==0.104.1
uvicorn==0.24.0
openai==1.3.0
faiss-cpu==1.7.4
beautifulsoup4==4.12.2
requests==2.31.0
pydantic==2.5.0
numpy==1.24.3
```

## 🔧 Configuration values

Edit these variables in `main.py`:

```python
START_URL = "https://www.w3schools.com/python/"  # Website to crawl
MAX_PAGES = 15                                    # Maximum pages to crawl
CHUNK_SIZE = 400                                  # Words per chunk
CHUNK_OVERLAP = 100                               # Overlap between chunks
```

## 📡 API Endpoints

### 1. Health Check
```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "status": "healthy",
  "message": "RAG Q&A Bot is running",
  "chunks": 150
}
```

### 2. Ask a Question
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Python?"}'
```

**Response:**
```json
{
  "answer": "Python is a high-level programming language...",
  "sources": [
    {
      "url": "https://www.w3schools.com/python/python_intro.asp",
      "title": "Python Introduction",
      "relevance": 0.95
    }
  ]
}
```

### 3. Get Statistics
```bash
curl http://localhost:8000/stats
```

**Response:**
```json
{
  "total_chunks": 150,
  "total_pages": 15,
  "embedding_dimension": 1536
}
```

## 💻 Usage Examples

### Python Client

```python
import requests

# Ask a question
response = requests.post(
    "http://localhost:8000/ask",
    json={"question": "How do I create a list in Python?"}
)

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}")
```

### cURL

```bash
# Simple question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What are Python variables?"}'
```

### JavaScript/Fetch

```javascript
const response = await fetch('http://localhost:8000/ask', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    question: 'What is a Python function?'
  })
});

const data = await response.json();
console.log(data.answer);
```

## 🔍 How It Works

### RAG  Pipeline (Overview)
1. **Crawling**: Start from `START_URL`, follow internal links up to `MAX_PAGES`.
2. **Text Extraction**: Use BeautifulSoup to extract and clean text.
3. **Chunking**: Split text into chunks of `CHUNK_SIZE` words with `CHUNK_OVERLAP`.
4. **Embedding**: Generate embeddings for each chunk using OpenAI's API.
5. **Vector Store**: Store embeddings in FAISS for efficient similarity search.
6. **Query Handling**:
   - Receive question via FastAPI.
   - Generate embedding for the question.
   - Retrieve top relevant chunks from FAISS.
   - Use GPT-4 to generate an answer based solely on retrieved chunks.
   - Return answer and source metadata.
   - Expose endpoints for health check and stats.

```

## 🛠️ Development Tips

```bash
pip install -r requirements.txt
```

```bash
python main.py --port 8000
```

Or kill the process using port 8000:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Common Issues: 

## "Vector store not initialized"
Vector store not ready: wait 1–2 minutes for crawling and index building.

## "Rate limit exceeded"
Rate limits: reduce MAX_PAGES or wait; OpenAI limits may apply.

## 🔒 Security

- **Never commit** your OpenAI API key to GitHub
- Add `.env` to `.gitignore`
- Use environment variables for secrets
- Consider using `.env` file with `python-dotenv`:

```python
from dotenv import load_dotenv
load_dotenv()
```

## 📈 Scaling suggestions

### For Production considerations:

1. Persisting cached embeddings to disk or database
2. Asynchronous and concurrent crawling
3. Rate limiting client requests
4. Moving from FAISS in-memory to a durable store (e.g., PostgreSQL with pgvector)
5. Adding authentication and monitoring
6. Containerizing with Docke

### Example Production Architecture:

```
┌─────────┐     ┌──────────┐     ┌─────────┐
│  NGINX  │────▶│ FastAPI  │────▶│  FAISS  │
└─────────┘     └──────────┘     └─────────┘
                     │
                     ▼
                ┌─────────┐
                │ OpenAI  │
                │   API   │
                └─────────┘
```

```

## 📝 Sample questions to try

- "What is Python?"
- "How do I create a list?"
- "What are Python functions?"
- "How do loops work in Python?"
- "What is a Python dictionary?"
- "How do I handle errors in Python?"

---
