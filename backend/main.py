import os
import random
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from db import supabase
from models import SignupRequest, ScheduleResponse

app = FastAPI()

# --- Helpers ---

def get_now():
    return datetime.now(timezone.utc)

def fetch_event(event_id: str):
    response = supabase.table("events").select("*").eq("id", event_id).single().execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Event not found")
    return response.data

def fetch_counts(event_id: str):
    # This is a bit inefficient doing client-side counting, but fine for MVP
    # Ideally use a .count() query
    roster = supabase.table("event_signups").select("id", count="exact").eq("event_id", event_id).eq("list_type", "EVENT").execute()
    return roster.count

def get_max_holding_sequence(event_id: str) -> int:
    response = supabase.table("event_signups").select("sequence_number").eq("event_id", event_id).eq("list_type", "WAITLIST_HOLDING").order("sequence_number", desc=True).limit(1).execute()
    if response.data and response.data[0]['sequence_number']:
        return response.data[0]['sequence_number']
    return 0

# --- Routes ---

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Backend is running"}

@app.post("/api/signup")
async def signup(body: SignupRequest):
    # 1. Fetch Event & User
    event = fetch_event(body.event_id)
    user_id = body.user_id # In production, verify this matches auth token
    
    # Check if already signed up
    existing = supabase.table("event_signups").select("*").eq("event_id", body.event_id).eq("user_id", user_id).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="User already signed up")

    profile_res = supabase.table("profiles").select("*, user_groups(id)").eq("id", user_id).single().execute()
    profile = profile_res.data
    
    if not profile:
        raise HTTPException(status_code=400, detail="User profile not found")

    is_member = profile.get("user_groups") is not None
    
    # 2. Logic
    now = get_now()
    
    # Parse event times (assuming ISO strings from DB)
    # Supabase returns ISO strings. We compare as strings or helper objects
    # Ideally standardise, but simpler comparison:
    def to_dt(iso_str):
        return datetime.fromisoformat(iso_str.replace('Z', '+00:00'))

    roster_open = to_dt(event['roster_sign_up_open'])
    reserve_open = to_dt(event['reserve_sign_up_open'])
    initial_reserve = to_dt(event['initial_reserve_scheduling'])
    final_reserve = to_dt(event['final_reserve_scheduling'])
    max_signups = event['max_signups']

    target_list = "EVENT"
    sequence = None
    
    current_roster_count = fetch_counts(body.event_id)

    if is_member:
        # Members Logic
        if now < roster_open:
             raise HTTPException(status_code=400, detail="Roster signup not yet open")
        
        if current_roster_count < max_signups:
            target_list = "EVENT"
            # Sequence: simple append logic handled by DB ID or explicit if needed.
            # Frontend used 'eventList.length + 1'. We will follow that or leave null.
            # Let's count explicitly for sequence
            target_list_count = fetch_counts(body.event_id) # Re-fetch?? optimize later
            sequence = target_list_count + 1
        else:
            target_list = "WAITLIST"
            # count waitlist
            wl_res = supabase.table("event_signups").select("id", count="exact").eq("event_id", body.event_id).eq("list_type", "WAITLIST").execute()
            sequence = wl_res.count + 1

    else:
        # Guest Logic
        if now < reserve_open:
            raise HTTPException(status_code=400, detail="Reserve signup not yet open")
        
        elif now < initial_reserve:
            # Window 1: Holding (Blind)
            target_list = "WAITLIST_HOLDING"
            sequence = -1 # Representing null/dash
            
        elif now < final_reserve:
            # Window 2: Holding (Sequenced)
            target_list = "WAITLIST_HOLDING"
            max_seq = get_max_holding_sequence(body.event_id)
            sequence = max_seq + 1
            
        else:
            # After Final: Normal access
            if current_roster_count < max_signups:
                target_list = "EVENT"
                sequence = current_roster_count + 1
            else:
                target_list = "WAITLIST"
                wl_res = supabase.table("event_signups").select("id", count="exact").eq("event_id", body.event_id).eq("list_type", "WAITLIST").execute()
                sequence = wl_res.count + 1

    # 3. Execute Insert
    payload = {
        "event_id": body.event_id,
        "user_id": user_id,
        "list_type": target_list,
        "sequence_number": sequence
    }
    
    res = supabase.table("event_signups").insert(payload).execute()
    return {"status": "success", "data": res.data[0]}


@app.post("/api/schedule")
async def trigger_schedule():
    """
    Auto-schedule guests from Holding Area -> Event/Waitlist
    Run this periodically or trigger manually.
    """
    now = get_now()
    now_iso = now.isoformat()
    
    # 1. Find Events ready for processing
    # Status is SCHEDULED AND final_reserve_scheduling <= now
    # We could also add a flag "processed" to avoid re-running, but idempotency is better.
    events_res = supabase.table("events")\
        .select("*")\
        .eq("status", "SCHEDULED")\
        .lte("final_reserve_scheduling", now_iso)\
        .execute()
        
    events = events_res.data
    processed_count = 0
    
    for event in events:
        event_id = event['id']
        max_signups = event['max_signups']
        
        # Check for Holding users
        holding_res = supabase.table("event_signups")\
            .select("*")\
            .eq("event_id", event_id)\
            .eq("list_type", "WAITLIST_HOLDING")\
            .execute()
            
        holding_users = holding_res.data
        if not holding_users:
            continue
            
        # 2. Sort Logic
        # Window 1 (seq -1) -> Random Shuffle
        # Window 2 (seq > 0) -> Sorted by seq
        window1 = [u for u in holding_users if not u.get('sequence_number') or u.get('sequence_number') < 0]
        window2 = [u for u in holding_users if u.get('sequence_number') and u.get('sequence_number') > 0]
        
        # Shuffle Window 1
        random.shuffle(window1)
        
        # Sort Window 2
        window2.sort(key=lambda x: x['sequence_number'])
        
        queue = window1 + window2
        
        # 3. Promote
        # We need current roster count *right now*
        roster_res = supabase.table("event_signups").select("id", count="exact").eq("event_id", event_id).eq("list_type", "EVENT").execute()
        current_roster_count = roster_res.count or 0
        
        waitlist_res = supabase.table("event_signups").select("id", count="exact").eq("event_id", event_id).eq("list_type", "WAITLIST").execute()
        current_waitlist_count = waitlist_res.count or 0
        
        for user in queue:
            signup_id = user['id']
            new_list = "EVENT"
            new_seq = 0
            
            if current_roster_count < max_signups:
                new_list = "EVENT"
                current_roster_count += 1
                new_seq = current_roster_count
            else:
                new_list = "WAITLIST"
                current_waitlist_count += 1
                new_seq = current_waitlist_count
                
            # Update DB
            supabase.table("event_signups").update({
                "list_type": new_list,
                "sequence_number": new_seq
            }).eq("id", signup_id).execute()
            
            processed_count += 1

    return {"status": "completed", "processed_events": len(events), "users_promoted": processed_count}


# Serve React App (SPA)
app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    file_path = f"static/{full_path}"
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse("static/index.html")
