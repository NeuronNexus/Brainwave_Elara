"""
runtime_sandbox/templates.py
"""

DOCKERFILE_TEMPLATES = {
    "python": """
FROM python:3.11-slim
RUN useradd -m appuser
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || echo "Pip install warning"
COPY . .
USER appuser
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
EXPOSE 8000 5000 8501
CMD {start_command}
""",

    "node": """
FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm install --only=production || echo "NPM install failed"
COPY . .
USER node
ENV PORT=3000
EXPOSE 3000 8080
CMD {start_command}
"""
}

GENERIC_TEMPLATE = """
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y bash curl
WORKDIR /app
COPY . .
ENV PORT=8080
EXPOSE 8080
CMD {start_command}
"""