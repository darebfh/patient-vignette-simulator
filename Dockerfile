FROM python:3.10-slim-bullseye



RUN apt-get update && apt-get install -y  \
    #gcc \
   # python3-dev \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /opt/app/requirements.txt
WORKDIR /opt/app
RUN pip install -r requirements.txt
COPY . /opt/app

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health


ENTRYPOINT ["streamlit", "run", "src/streamlit/Chat.py", "--server.port=8501", "--server.address=0.0.0.0"]