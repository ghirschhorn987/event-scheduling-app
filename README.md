# Event Scheduling App (Full Stack)

This project has been restructured to support a **React Frontend** and a **Python (FastAPI) Backend**, deployable as a single container on **Google Cloud Run**.

## Project Structure

- `frontend/`: The React application (Vite).
- `backend/`: The Python FastAPI application.
- `database/`: Database SQL schemas and scripts.
- `Dockerfile`: Multi-stage build for deploying everything together.

## Local Development

### 1. Run Frontend (React)
Navigate to the frontend directory:
```bash
cd frontend
npm install
npm run dev
```
The frontend runs on `http://localhost:5173`.

### 2. Run Backend (Python)
Navigate to the backend directory:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```
The backend runs on `http://localhost:8000`.

> **Note**: In local development, the frontend talks to Supabase directly. To call the backend you may need to configure proxying in `vite.config.js` or use full URLs.

## Deployment (Google Cloud Run)

Prerequisites: `gcloud` CLI installed and authenticated.

1. **Deploy using Cloud Build & Run**:
   ```bash
   gcloud run deploy event-scheduling-app \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

   This command will:
   - Upload your code.
   - Build the Docker container (using the `Dockerfile` in root).
   - Deploy it to a HTTPS URL.

2. **Environment Variables**:
   You can set Supabase keys in the Cloud Run dashboard or via command line flags:
   ```bash
   --set-env-vars SUPABASE_URL=...,SUPABASE_KEY=...
   ```

## Architecture

In the deployed container:
- **FastAPI** serves as the web server.
- It handles API requests at `/api/*`.
- It serves the compiled React app (`index.html` and assets) for all other routes.
