# AWS Customer Agreement RAG Assistant

A robust, end-to-end Retrieval-Augmented Generation (RAG) application designed to answer questions specifically about the AWS Customer Agreement. Built with FastAPI for the backend and Streamlit for a highly interactive frontend dashboard.

## 🚀 Features

* **Intelligent Q&A**: Uses Google's `gemini-2.5-flash` model and LangChain to provide accurate, context-aware answers based strictly on the provided AWS Customer Agreement PDF.
* **Vector Search**: Embeddings are generated using HuggingFace's `all-MiniLM-L6-v2` and stored locally using ChromaDB for lightning-fast retrieval.
* **Analytics Dashboard**: A built-in Streamlit dashboard powered by Plotly to track total queries, success rates, average latency, and most frequent questions.
* **Automated Testing & Data Generation**: Includes a "Magic Button" in the UI and an `auto_test.py` script to automatically generate 30+ varied test queries to populate the analytics dashboard.
* **Source Transparency**: Every answer includes an expandable section showing the exact source text chunks retrieved from the document, along with confidence scores and latency metrics.

## 🏛️ Architecture Overview

User Question
      ↓
Streamlit Frontend
      ↓
FastAPI Backend
      ↓
ChromaDB Retrieval
      ↓
Top-K Relevant Chunks
      ↓
Gemini 2.5 Flash
      ↓
Answer + Sources
      ↓
SQLite Logging
      ↓
Analytics Dashboard

## 🧩 Chunking Strategy

* **Chunk Size**: 800 characters
* **Chunk Overlap**: 100 characters

**Reason**: 
A chunk size of 800 preserves semantic context while remaining efficient for retrieval. A 100-character overlap reduces information loss at chunk boundaries and improves retrieval quality.

## 🔍 Retrieval Strategy

* **Embedding Model**: `all-MiniLM-L6-v2`
* **Vector Store**: ChromaDB
* **Top-K Retrieval**: 4

**Reason**: 
Top-4 retrieval balances context quality and token usage, providing sufficient information for answer generation without introducing excessive noise.

## 🗄️ SQL Logging Schema

The application logs all queries in a local SQLite database table named `query_logs`:

* `id`
* `question`
* `answer`
* `answer_found`
* `response_time`
* `timestamp`

## 🛡️ Error Handling

The system implements strict validation and error handling across multiple layers:
* Empty Query Validation
* Missing PDF Detection
* Missing Vector Store Detection
* Gemini API Failure Handling
* Database Error Handling

## 🛠️ Technology Stack

* **Frontend**: Streamlit, Plotly, Pandas
* **Backend**: FastAPI, Uvicorn, SQLite
* **AI / RAG**: LangChain, Google Gemini API, HuggingFace (`sentence-transformers`), ChromaDB, PyPDF

## 📦 Installation & Setup

### 1. Clone the repository
Ensure you have Python 3.12+ installed. 
*(Note for Windows users: Use `py` instead of `python` in the commands below).*

### 2. Install dependencies
```bash
py -m pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory and add your Google Gemini API Key:
```env
GEMINI_API_KEY="your_api_key_here"
```

### 4. Place the Data File
Ensure your PDF file is named exactly `AWS Customer Agreement.pdf` and is placed in the root directory of the project.

## 🏃‍♂️ Running the Application

This application requires both the FastAPI backend and the Streamlit frontend to be running simultaneously in separate terminal windows.

### Step 1: Start the Backend (FastAPI)
Open a terminal and run:
```bash
py -m uvicorn main:app --host 127.0.0.1 --port 8000
```
*The backend will be available at http://127.0.0.1:8000*

### Step 2: Start the Frontend (Streamlit)
Open a **new** terminal tab/window and run:
```bash
py -m streamlit run app.py --browser.gatherUsageStats=false
```
*The Streamlit interface will open in your browser at http://localhost:8501*

## 💡 How to Use

1. **Ingest Document**: On the Streamlit Chat Interface, click the **"Ingest Document (Run Once)"** button. This will parse the PDF, generate embeddings, and save them to ChromaDB.
2. **Ask Questions**: Type your questions into the chat input. Try asking "What is the governing law for Australia?" or "How does AWS handle data privacy?"
3. **Analytics**: Switch to the **Analytics Dashboard** using the left sidebar to view system performance and query metrics.
4. **Developer Tools**: Click the **"Generate 30 Test Queries"** button in the sidebar to automatically populate your database with sample queries for the analytics dashboard.

## 🚀 Future Enhancements

* Multi-document support
* User authentication
* PDF upload support
* Hybrid search (BM25 + Vector Search)
* Advanced analytics

## ⚠️ Important Notes
* **API Rate Limits**: If using the Free Tier of the Gemini API, be careful when using the automated testing tools, as generating 30 queries rapidly may hit Google's `429 Too Many Requests` limit.
* **Database**: All query logs and analytics are stored locally in a SQLite database inside the `/data` folder. Vector embeddings are stored in `/vectorstore`.
