# Groq + ChromaDB RAG Assistant

A fast, modular, and privacy-focused Retrieval-Augmented Generation (RAG) system built with **Groq LLM**, **ChromaDB**, **FastAPI**, and **SentenceTransformers**.

This project provides end-to-end document question-answering with **100% free local embeddings** for document chunking and vector indexing, leveraging the **Groq API** exclusively for ultra-fast response generation.

---

## 🖼️ Application Preview

### Web UI Dashboard
![Web Dashboard](assets/web_ui.png)

### Terminal / CLI Interface
![CLI Demo](assets/cli_demo.png)

---

## 🌟 Key Features

* ⚡ **Ultra-Fast Answer Generation**: Powered by the Groq API using the `openai/gpt-oss-20b` model.
* 🔒 **Free Local Embeddings**: Runs `sentence-transformers/all-MiniLM-L6-v2` locally via Hugging Face—no external API keys required for vector embeddings.
* 📂 **Multi-Format Support**: Native ingestion for `.pdf`, `.txt`, and `.md` document types.
* 🧩 **Smart Chunking & Ingestion**: Custom sliding-window text chunking with deterministic SHA-256 chunk hashing to avoid duplication.
* 🖥️ **Full-Stack Interfaces**:
  * **Web Dashboard**: Responsive web interface (`templates/index.html`) served directly by FastAPI with custom CSS (`static/style.css`).
  * **REST API**: Production-ready FastAPI endpoints with automated OpenAPI (`/docs`) interactive documentation.
  * **Interactive CLI**: Terminal-based client (`cli.py`) for instant testing and debugging.

---

## 🏗️ System Architecture

```text
               +----------------------------------+
               |   Documents (.pdf, .txt, .md)    |
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               |   Text Extraction & Chunking     |
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               | SentenceTransformers (Local CPU) |
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               |  ChromaDB DB (./chorama_db)      |
               +----------------------------------+

                                ^
                                | Similarity Search
                                |
User Question ---> [ Local Query Embedding ]
                                |
                                v
                   +--------------------------+
                   |  Top-K Retrieved Chunks  |
                   +--------------------------+
                                |
                                v
                   +--------------------------+
                   | Groq API (openai/gpt-oss) |
                   +--------------------------+
                                |
                                v
                   +--------------------------+
                   | Grounded Answer + Source |
                   +--------------------------+
```

---

## 📁 Directory Structure

```text
groq_chromadb_rag/
├── app/
│   ├── chunker.py           # Text chunking and sliding window logic
│   ├── config.py            # Settings dataclass & env validation
│   ├── document_loader.py   # Loaders for PDF, TXT, and Markdown files
│   ├── embedding_service.py # Local SentenceTransformer model service
│   ├── groq_service.py      # Integration with Groq API for LLM generation
│   ├── ingest_service.py   # Ingestion runner and vector store pipeline
│   ├── rag_service.py       # Core RAG retrieval and prompt context builder
│   └── vector_store.py      # Persistent ChromaDB client wrapper
├── assets/                  # Folder for working app screenshots (web_ui.png, cli_demo.png)
├── data/                    # Storage directory for source documents (.pdf, .txt, .md)
├── static/                  # Web styling assets (style.css)
├── templates/               # Web application UI (index.html)
├── .env.example             # Environment template file
├── api.py                   # FastAPI server entry point
├── cli.py                   # Interactive command-line interface
├── ingest.py                # Command-line document ingestion runner
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

---

## ⚙️ Environment Configuration

Create a `.env` file in the root directory by copying `.env.example`:

```bash
cp .env.example .env
```

Configure your parameters in `.env`:

```env
# Groq API Configuration
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b

# Free Local Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Vector Store Settings
CHROMA_PATH=./chorama_db
CHROMA_COLLECTION=Knowledge_base

# Retrieval & Chunking Parameters
TOP_K=5
CHUNK_SIZE=1200
CHUNK_OVERLAP=200
EMBEDDING_BATCH_SIZE=64
```

> **Note:** Obtain your free API key from the [Groq Console](https://console.groq.com).

---

## 📦 Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/groq_chromadb_rag.git
cd groq_chromadb_rag
```

### 2. Create Virtual Environment

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🚀 How to Run

### Step 1: Ingest Documents

Place your source files (`.pdf`, `.txt`, `.md`) inside the `data/` directory, then execute the ingestion pipeline:

```bash
# Ingest new documents
python ingest.py

# Reset ChromaDB collection and re-index everything:
python ingest.py --reset
```

### Step 2: Interactive Terminal Mode (CLI)

Run queries directly in your terminal:

```bash
python cli.py
```

### Step 3: Launch Web App & REST API Server

Start the application server using Uvicorn:

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

* **Web UI Dashboard**: Access at `http://127.0.0.1:8000`
* **Interactive Swagger Docs**: Access at `http://127.0.0.1:8000/docs`

---

## 📡 API Reference Example

**Endpoint:** `POST /rag/query`

**Request Body:**

```json
{
  "question": "What is an embedding?",
  "top_k": 5
}
```

**Filter Request by Document Source:**

```json
{
  "question": "What is the net profit mentioned in the financial report?",
  "top_k": 3,
  "source": "finance_report.txt"
}
```

**Sample Response:**

```json
{
  "question": "What is an embedding?",
  "answer": "An embedding is a numerical vector representation of text that captures its semantic meaning...",
  "sources": [
    {
      "source": "sample.txt",
      "page": 0,
      "chunk": 0,
      "distance": 0.1245,
      "text": "An embedding is a vector of numbers that represents the semantic meaning of text."
    }
  ]
}
```