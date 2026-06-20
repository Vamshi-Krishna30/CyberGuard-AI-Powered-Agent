FROM python:3.11-slim

WORKDIR /app

# సిస్టమ్ డిపెండెన్సీస్ ఇన్‌స్టాల్ చేయడం
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Cache ని యూస్ చేసుకుంటూ ప్యాకేజీలు ఇన్‌స్టాల్ చేయడం
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# మిగతా కోడ్ ఫైల్స్ అన్నీ కాపీ చేయడం
COPY . .

# Hugging Face Spaces కోసం ఎన్విరాన్మెంట్ వేరియబుల్స్
ENV STREAMLIT_SERVER_PORT=7860
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_HEADLESS=true

EXPOSE 7860

# సింపుల్ అండ్ క్లీన్ రన్ కమాండ్
CMD ["streamlit", "run", "app.py"]