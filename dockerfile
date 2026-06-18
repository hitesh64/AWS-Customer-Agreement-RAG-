FROM python:3.11-slim

WORKDIR /app

# 1. Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 🚀 PRO TRICK: Pre-download the AI model during build time so it starts instantly later!
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# 2. Copy all your project files into the container
COPY . .

# 3. Create a startup script to run both FastAPI and Streamlit
RUN echo '#!/bin/bash\n\
uvicorn main:app --host 0.0.0.0 --port 8000 & \n\
sleep 5\n\
streamlit run app.py --server.port 7860 --server.address 0.0.0.0\n\
' > start.sh

RUN chmod +x start.sh

# 4. Expose the port Hugging Face expects
EXPOSE 7860

# 5. Run the script
CMD ["./start.sh"]