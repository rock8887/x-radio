FROM python:3.11

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN playwright install --with-deps chromium

COPY . .

EXPOSE 10000

CMD streamlit run app.py --server.port 10000 --server.address 0.0.0.0
