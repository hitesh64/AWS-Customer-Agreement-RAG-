import os
import json
import logging
import time
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from config import PDF_PATH, CHROMA_PATH, CHUNK_SIZE, CHUNK_OVERLAP, TOP_K, GEMINI_API_KEY

logger = logging.getLogger(__name__)

embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GEMINI_API_KEY, temperature=0.0)

def ingest_document():
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"PDF document not found at {PDF_PATH}")

    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings_model,
        persist_directory=CHROMA_PATH
    )
    return len(chunks)

def process_query(question: str):
    start_time = time.time()
    
    if not os.path.exists(CHROMA_PATH):
        raise ValueError("Vector database not initialized. Please call /ingest first.")

    vectorstore = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings_model)
    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})
    
    retrieved_docs = retriever.invoke(question)
    context_text = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
    sources = [doc.page_content for doc in retrieved_docs]

    prompt = f"""
    You are an expert legal assistant analyzing the AWS Customer Agreement. 
    Use the following retrieved context to answer the user's question.
    If the answer is NOT present in the context, you MUST reply EXACTLY with: "The answer is not available in the provided document." Do not hallucinate.
    
    Return your response in strictly valid JSON format with two keys:
    - "answer": (string) Your detailed answer or the exact not available phrase.
    - "confidence": (float) A score between 0.0 and 1.0 representing your confidence based on the context. If not found, confidence is 0.0.
    Context:
    {context_text}
    Question:
    {question}
    """

    try:
        response = llm.invoke(prompt)
        response_text = response.content.strip().replace("```json", "").replace("```", "")
        parsed_response = json.loads(response_text)
        
        answer = parsed_response.get("answer", "Error parsing answer.")
        confidence = float(parsed_response.get("confidence", 0.0))
        
        target_phrase = "The answer is not available in the provided document."
        answer_found = target_phrase.lower() not in answer.lower()

    except Exception as e:
        logger.error(f"LLM Error: {e}")
        answer = "The answer is not available in the provided document."
        confidence = 0.0
        answer_found = False

    response_time = round(time.time() - start_time, 4)

    return {
        "answer": answer,
        "sources": sources if answer_found else [],
        "confidence": confidence,
        "response_time": response_time,
        "answer_found": answer_found
    }