import requests
import time

# Ingest document first to ensure vector DB is ready
print("Ensuring document is ingested first...")
try:
    ingest_resp = requests.post("http://127.0.0.1:8000/ingest", timeout=60)
    if ingest_resp.status_code == 201:
        print("[SUCCESS] Document successfully ingested!\n")
    else:
        print(f"[WARN] Ingestion responded with {ingest_resp.status_code}. It might already be ingested.\n")
except Exception as e:
    print(f"Failed to call /ingest: {e}\n")

# Aapka FastAPI backend ka URL
API_URL = "http://127.0.0.1:8000/ask"

# 30+ Questions ka mix (Valid + Invalid)
test_queries = [
    # --- VALID AWS QUESTIONS (In-Scope) ---
    "What is the AWS Customer Agreement?",
    "When does the agreement become effective?",
    "Who is the contracting party for India?",
    "What are the payment obligations?",
    "How does AWS handle data privacy?",
    "Can I terminate the agreement for convenience?",
    "What is the governing law for Australia?",
    "Are there any Service Level Agreements (SLAs)?",
    "What happens to my content after termination?",
    "Who pays for indirect taxes?",
    "Is AWS liable for indirect damages?",
    "How much notice is given before a service is discontinued?",
    "How are disputes resolved in Mexico?",
    "What is the Acceptable Use Policy?",
    "Does AWS own my content?",
    "What is the damage cap under this agreement?",
    "How do I notify AWS?",
    "What happens if I breach the agreement?",
    "Are there trade compliance rules?",
    "Who is responsible for backing up data?",
    "Can I transfer my account to someone else?",
    
    # --- INVALID QUESTIONS (Out-of-Scope) ---
    "Who won IPL 2026?",
    "What is the recipe for white sauce pasta?",
    "Tell me about Elon Musk.",
    "What is the current weather in Nagpur?",
    "How to build a React JS application?",
    "Who is the CEO of Tesla?",
    "What is the price of Bitcoin today?",
    "Summarize the plot of the movie Inception.",
    "Write a Python script for web scraping.",
    "How do I repair a punctured bicycle tire?",
    "What are the rules of playing cricket?",
]

print(f"Starting automated testing with {len(test_queries)} queries...\n")

for i, query in enumerate(test_queries, 1):
    print(f"[{i}/{len(test_queries)}] Asking: {query}")
    try:
        # Note: Agar aapke schemas.py mein variable ka naam 'query' ya 'text' hai, toh "question" ko replace kar lena.
        payload = {"question": query} 
        
        response = requests.post(API_URL, json=payload, timeout=30)
        
        if response.status_code == 200:
            print("[SUCCESS] Success!")
        else:
            print(f"[FAIL] Failed with status code: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Connection Error: {e}")
    
    # Backend par overload na ho isliye 2 second ka pause
    time.sleep(2)

print("\n[DONE] All queries executed! Apna Streamlit Dashboard check kijiye.")
