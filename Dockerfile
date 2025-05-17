# --- STEG 1: Bygg frontend (Vue + Vite) ---
FROM node:18 AS frontend-builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# --- STEG 2: Python-backend med Flask ---
FROM python:3.10-slim

RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=frontend-builder /app/dist /app/dist
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "API_server.py"]
