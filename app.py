import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AWS Agreement Q&A", layout="wide")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def chat_interface():
    st.title("📄 AWS Customer Agreement Assistant")
    st.markdown("Ask any questions regarding the AWS Customer Agreement.")

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Ingest Document (Run Once)"):
            with st.spinner("Ingesting document..."):
                resp = requests.post(f"{API_BASE_URL}/ingest")
                if resp.status_code == 201:
                    st.success("Document ingested successfully!")
                else:
                    st.error(f"Error: {resp.text}")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("sources"):
                with st.expander("View Source Chunks & Metadata"):
                    st.markdown(f"**Confidence:** {msg['confidence']*100:.2f}% | **Latency:** {msg['latency']}s")
                    for i, source in enumerate(msg["sources"]):
                        st.info(f"**Source {i+1}:**\n{source}")

    if prompt := st.chat_input("Enter your question..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching the agreement..."):
                try:
                    response = requests.post(f"{API_BASE_URL}/ask", json={"question": prompt})
                    if response.status_code == 200:
                        data = response.json()
                        answer = data["answer"]
                        sources = data["sources"]
                        latency = data["response_time"]
                        confidence = data["confidence"]
                        
                        st.markdown(answer)
                        if sources:
                            with st.expander("View Source Chunks & Metadata"):
                                st.markdown(f"**Confidence:** {confidence*100:.2f}% | **Latency:** {latency}s")
                                for i, source in enumerate(sources):
                                    # Basic source highlighting logic
                                    st.info(f"**Source {i+1}:**\n{source}")
                                    
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": answer,
                            "sources": sources,
                            "latency": latency,
                            "confidence": confidence
                        })
                    else:
                        error_msg = response.json().get("detail", "Unknown error")
                        st.error(f"Backend Error: {error_msg}")
                except Exception as e:
                    st.error("Failed to connect to the backend API. Ensure FastAPI is running.")

    if st.session_state.chat_history:
        df_export = pd.DataFrame(st.session_state.chat_history)
        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Download Chat History CSV", data=csv, file_name='chat_history.csv', mime='text/csv')

def analytics_dashboard():
    st.title("📊 System Analytics Dashboard")
    
    if st.button("Refresh Analytics"):
        st.rerun()

    try:
        resp = requests.get(f"{API_BASE_URL}/analytics")
        if resp.status_code == 200:
            data = resp.json()
            
            # Key Metrics
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Queries", data["total_queries"])
            c2.metric("No Answer Found", data["no_answer_queries"])
            c3.metric("Avg Latency (s)", f"{data['average_latency']:.2f}")
            success_rate = 0 if data['total_queries'] == 0 else ((data['total_queries'] - data['no_answer_queries']) / data['total_queries']) * 100
            c4.metric("Answer Success Rate", f"{success_rate:.1f}%")

            st.markdown("---")
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Frequent Questions")
                freq_data = data["most_frequent_questions"]
                if freq_data:
                    df_freq = pd.DataFrame(freq_data)
                    fig = px.bar(df_freq, x="count", y="question", orientation='h', title="Top 5 Questions")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Not enough data.")

            with col2:
                st.subheader("Answer Found vs Not Found")
                status_data = data["found_vs_not_found"]
                if status_data:
                    df_status = pd.DataFrame(status_data)
                    fig2 = px.pie(df_status, values='count', names='status', title="Query Resolution Breakdown")
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("Not enough data.")
                    
            csv_analytics = pd.json_normalize(data).to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 Download Analytics Report", data=csv_analytics, file_name='analytics_report.csv', mime='text/csv')

        else:
            st.error("Failed to retrieve analytics.")
    except Exception:
        st.error("Failed to connect to the backend API. Ensure FastAPI is running.")

pages = {
    "Chat Interface": chat_interface,
    "Analytics Dashboard": analytics_dashboard
}

st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(pages.keys()))
pages[selection]()

# === MAGIC BUTTON FOR 30 QUERIES ===
st.sidebar.markdown("---")
st.sidebar.subheader("🚀 Developer Tools")
if st.sidebar.button("Generate 30 Test Queries (For Analytics)"):
    test_queries = [
        "What is the AWS Customer Agreement?", "When does the agreement become effective?",
        "Who is the contracting party for India?", "What are the payment obligations?",
        "How does AWS handle data privacy?", "Can I terminate the agreement for convenience?",
        "What is the governing law for Australia?", "Are there any Service Level Agreements (SLAs)?",
        "What happens to my content after termination?", "Who pays for indirect taxes?",
        "Is AWS liable for indirect damages?", "How much notice is given before a service is discontinued?",
        "How are disputes resolved in Mexico?", "What is the Acceptable Use Policy?",
        "Does AWS own my content?", "What is the damage cap under this agreement?",
        "How do I notify AWS?", "What happens if I breach the agreement?",
        "Are there trade compliance rules?", "Who is responsible for backing up data?",
        "Can I transfer my account to someone else?", "Who won IPL 2026?",
        "What is the recipe for white sauce pasta?", "Tell me about Elon Musk.",
        "What is the current weather in Nagpur?", "How to build a React JS application?",
        "Who is the CEO of Tesla?", "What is the price of Bitcoin today?",
        "Summarize the plot of the movie Inception.", "Write a Python script for web scraping."
    ]
    
    progress_bar = st.sidebar.progress(0)
    status_text = st.sidebar.empty()
    
    for i, query in enumerate(test_queries):
        status_text.text(f"Processing ({i+1}/30): {query[:20]}...")
        try:
            # Same payload as your actual frontend uses
            requests.post(f"{API_BASE_URL}/ask", json={"question": query}, timeout=15)
        except Exception as e:
            pass # Ignore connection timeouts to keep it fast
        
        progress_bar.progress((i + 1) / len(test_queries))
        
    status_text.text("✅ Data Generated! Please refresh dashboard.")
# ===================================