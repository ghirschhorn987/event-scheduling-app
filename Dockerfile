# Build Stage for React
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend

# Install node dependencies
COPY frontend/package*.json ./
RUN npm ci

# Copy source and build
COPY frontend/ ./
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_ANON_KEY
ARG VITE_USE_MOCK_AUTH
ENV VITE_SUPABASE_URL=$VITE_SUPABASE_URL
ENV VITE_SUPABASE_ANON_KEY=$VITE_SUPABASE_ANON_KEY
ENV VITE_USE_MOCK_AUTH=$VITE_USE_MOCK_AUTH
# Remove any existing dist folder to ensure clean build
RUN rm -rf dist
RUN npm run build

# Final Stage for Python
FROM python:3.11-slim
WORKDIR /app

# Install python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy built frontend assets to static folder
# Vite output is in dist/
COPY --from=frontend-builder /app/frontend/dist ./static

# Cloud Run expects the app to listen on local env $PORT
ENV PORT=8080

# Start command
# We use 'exec' to ensure signals are passed correctly
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
