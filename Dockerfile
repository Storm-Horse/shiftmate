# ── Stage 1: Build React frontend ─────────────────────────────────────────
FROM node:20-slim AS frontend
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ── Stage 2: Python API + static files ────────────────────────────────────
FROM python:3.12-slim
WORKDIR /app

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./

# Copy React build into backend/static so FastAPI can serve it
COPY --from=frontend /frontend/dist ./static

# /data is the persistent volume mount point for the SQLite database
RUN mkdir -p /data

EXPOSE 8000
CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}
