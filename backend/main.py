import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

# Placeholder for Supabase client
# from supabase import create_client, Client
# url: str = os.environ.get("SUPABASE_URL")
# key: str = os.environ.get("SUPABASE_KEY")
# supabase: Client = create_client(url, key)

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Backend is running"}

@app.post("/api/schedule")
async def trigger_schedule():
    # Placeholder for the complex scheduling logic
    return {"status": "scheduled", "details": "Logic to be implemented"}

# Serve React App (SPA)
# specific files first to avoid catching them with the wildcard
app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    # This acts as a catch-all for SPA routing.
    # If the file exists in static, serve it? 
    # Actually, StaticFiles is better for assets, but for the index.html fallback:
    file_path = f"static/{full_path}"
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # Fallback to index.html for React Router
    return FileResponse("static/index.html")
