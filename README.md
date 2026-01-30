# rag-ai-project - RAG Q&A Support Bot

A complete **Retrieval Augmented Generation (RAG)** system that crawls websites, generates embeddings using OpenAI, stores them in a FAISS vector database, and answers user questions using only the crawled content.

## 📁 Project Structure

```
rag-ai-project/
├── .github/              # GitHub configuration
├── .venv/                # Python virtual environment
├── main.py               # Main application file
├── README.md             # This file
└── requirements.txt      # Python dependencies
```

## 🎯 What This Project Does

This RAG bot:
1. **Crawls** a website (W3Schools Python tutorial)
2. **Cleans** the text content
3. **Chunks** text into manageable pieces
4. **Generates embeddings** using OpenAI API
5. **Stores** embeddings in FAISS vector database
6. **Retrieves** relevant content for user questions
7. **Generates answers** using GPT-4 based only on crawled content
8. **Serves** answers via FastAPI endpoint

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/ashutoshnawale89/rag-ai-project.git
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

## 📋 Requirements

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

## 🔧 Configuration

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

### RAG Workflow

```
┌─────────────┐
│  1. CRAWL   │  Scrape website pages
└──────┬──────┘
       │
┌──────▼──────┐
│  2. CLEAN   │  Remove scripts, nav, etc.
└──────┬──────┘
       │
┌──────▼──────┐
│  3. CHUNK   │  Split into 400-word chunks
└──────┬──────┘
       │
┌──────▼──────┐
│  4. EMBED   │  Generate OpenAI embeddings
└──────┬──────┘
       │
┌──────▼──────┐
│  5. STORE   │  Save in FAISS vector DB
└──────┬──────┘
       │
┌──────▼──────┐
│  6. QUERY   │  User asks question
└──────┬──────┘
       │
┌──────▼──────┐
│ 7. RETRIEVE │  Find similar chunks
└──────┬──────┘
       │
┌──────▼──────┐
│ 8. GENERATE │  GPT-4 generates answer
└─────────────┘
```

## 🛠️ Development

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

### Issue: "Vector store not initialized"
**Solution:** Wait for the startup process to complete. It takes 1-2 minutes to crawl and build the vector store.

### Issue: "Rate limit exceeded"
**Solution:** You've hit OpenAI API rate limits. Wait a few minutes or reduce `MAX_PAGES`.

## 🔒 Security Notes

- **Never commit** your OpenAI API key to GitHub
- Add `.env` to `.gitignore`
- Use environment variables for secrets
- Consider using `.env` file with `python-dotenv`:

```python
from dotenv import load_dotenv
load_dotenv()
```

## 📈 Scaling Considerations

### For Production:

1. **Cache embeddings**: Save to disk to avoid re-generating
2. **Use async**: Make crawling concurrent
3. **Add rate limiting**: Prevent API abuse
4. **Database**: Use PostgreSQL with pgvector instead of in-memory FAISS
5. **Authentication**: Add API key authentication
6. **Monitoring**: Add logging and metrics
7. **Docker**: Containerize the application

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

## 📝 Example Questions

Try asking:
- "What is Python?"
- "How do I create a list?"
- "What are Python functions?"
- "How do loops work in Python?"
- "What is a Python dictionary?"
- "How do I handle errors in Python?"

---

**Made with ❤️ for learning RAG systems**