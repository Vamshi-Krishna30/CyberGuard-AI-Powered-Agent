FROM python:3.11-slim

WORKDIR /app

# Minimal dependencies only
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only app.py
COPY app.py .

# HF Spaces config
ENV STREAMLIT_SERVER_PORT=7860
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

EXPOSE 7860

CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]