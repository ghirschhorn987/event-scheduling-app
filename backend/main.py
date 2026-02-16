import os
import random
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from db import supabase
from models import SignupRequest, ScheduleResponse, RegistrationRequest, RegistrationUpdate, GroupMemberAction, GroupMembersAction, UserGroupsUpdate, EventTypeCreate, EventTypeUpdate
from logic import enrich_event, randomize_holding_queue, promote_from_holding, check_signup_eligibility, determine_event_status, resequence_holding

app = FastAPI()

# --- Security Dependency ---

async def get_current_user(request: Request):
    """
    Validates the Authorization header and returns the user object.
    Raises 401 if invalid.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        # Check for Mock Mode via custom header or env (simplified for now)
        # In this environment, we just enforce Bearer token
        raise HTTPException(status_code=401, detail="Missing Authorization Header")
    
    token = auth_header.replace("Bearer ", "")
    
    # --- MOCK AUTHENTICATION START ---
    if os.environ.get("USE_MOCK_AUTH") == "true" and token.startswith("mock-token-"):
        # Format: mock-token-{role}-{id}
        # But for simplicity, we'll just check if it starts with mock-token- and trust the ID after it.
        # User ID is the rest of the string after "mock-token-"? NO.
        # The frontend uses: `mock-token-${user.id}`. So we strip "mock-token-".
        user_id = token.replace("mock-token-", "")
        # Return a "Fake" User object that quacks like a Supabase User
        # We need an object with .id, .email, etc.
        class MockUser:
            def __init__(self, uid):
                self.id = uid
                self.email = f"mock.{uid}@test.com"
                self.user_metadata = {"full_name": "Mock User"}
        
        print(f"DEBUG: Authenticated Mock User: {user_id}")
        return MockUser(user_id)
    # --- MOCK AUTHENTICATION END ---

    try:
        # Use simple get_user() verification
        user_res = supabase.auth.get_user(token)
        if not user_res.user:
             raise HTTPException(status_code=401, detail="Invalid Token")
        return user_res.user
    except Exception as e:
        print(f"Auth Error: {e}")
        raise HTTPException(status_code=401, detail="Invalid Authentication")

async def get_current_admin(request: Request):
    """
    Sub-dependency that ensures the user is an Admin.
    """
    user = await get_current_user(request)
    
    # Check Admin Status
    # Method 1: Check if email is in a whitelist (Simple, MVP)
    # Method 2: Check if user is in 'Admin' group in DB.
    # Method 3: Check 'user_metadata' for role claim.
    
    # We will use DB check on 'user_groups' or 'profiles'
    # But for today, checking email or Mock Role is safer/faster.
    # Let's check if they belong to "Admin" group (if exists) OR hardcoded email.
    
    if user.email == "mock.admin@test.com" or user.id == "793db7d3-7996-4669-8714-8340f784085c":
        return user
        
    # Real Check: Fetch Profile -> Groups
    # New Schema: profiles -> profile_groups -> user_groups
    try:
        res = supabase.table("profiles").select("*, profile_groups(user_groups(name))").eq("auth_user_id", user.id).single().execute()
        
        is_admin = False
        if res.data and res.data.get("profile_groups"):
            # profile_groups is a list of objects: [{'user_groups': {'name': 'Admin'}}, ...]
            for pg in res.data["profile_groups"]:
                if pg.get("user_groups"):
                    group_name = pg["user_groups"].get("name")
                    if group_name in ["Super Admin", "SuperAdmin", "Admin"]:
                        is_admin = True
                        break
        
        if is_admin:
            return user
    except Exception as e:
        print(f"Admin Check DB Error: {e}")
            
    # If not found
    print(f"Access Denied for user: {user.email} (ID: {user.id})")
    raise HTTPException(status_code=403, detail="Admin privileges required")

# --- Helpers ---

def get_now():
    return datetime.now(timezone.utc)



# enrich_event moved to logic.py

def fetch_event(event_id: str):
    # Join with event_types
    response = supabase.table("events").select("*, event_types(*)").eq("id", event_id).single().execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return enrich_event(response.data)

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

@app.post("/api/request-access")
async def request_access(body: RegistrationRequest):
    """
    Public endpoint for new users to request access.
    """
    # model_dump() is Pydantic v2
    payload = body.model_dump()
    
    # Check for duplicates? The DB unique constraint on email will handle it.
    try:
        # We use the Service Role Key (via 'supabase' client) so we can obtain write access 
        # even if RLS is strict (though we set RLS to allow public insert).
        res = supabase.table("registration_requests").insert(payload).execute()
        
        # Send Emails
        request_data = res.data[0]
        # Run in background? For MVP, synchronous valid.
        try:
            from email_service import email_service
            email_service.send_user_acknowledgement(request_data['email'], request_data['full_name'])
            email_service.send_admin_notification(request_data)
        except Exception as email_e:
            print(f"Failed to send email: {email_e}")

        return {"status": "success", "message": "Request received", "data": request_data}
    except Exception as e:
        print(f"Error creating request: {e}")
        # Improve error message if unique violation
        if "duplicate key" in str(e) or "unique constraint" in str(e):
             raise HTTPException(status_code=400, detail="A request with this email already exists.")
        raise HTTPException(status_code=400, detail="Failed to submit request.")

# --- Admin Routes ---

@app.get("/api/admin/requests")
async def list_requests(request: Request):
    user = await get_current_admin(request)
    
    # Fetch all pending requests
    # Sort by created_at desc
    res = supabase.table("registration_requests").select("*").order("created_at", desc=True).execute()
    return {"status": "success", "data": res.data}

@app.get("/api/admin/user_groups")
async def list_user_groups(request: Request):
    """
    Fetch all available user groups for the admin dropdown.
    """
    await get_current_admin(request)
    
    res = supabase.table("user_groups").select("*, profile_groups(count)").order("name").execute()
    
    # Flatten counts
    data = []
    for row in res.data:
        count = 0
        if row.get("profile_groups") and len(row["profile_groups"]) > 0:
            count = row["profile_groups"][0].get("count", 0)
        
        data.append({
            "id": row["id"],
            "name": row["name"],
            "description": row["description"],
            "google_group_id": row.get("google_group_id"),
            "user_count": count
        })
    return {"status": "success", "data": data}

@app.get("/api/admin/groups/{group_id}/members")
async def list_group_members(group_id: str, request: Request):
    await get_current_admin(request)
    # Join profile_groups -> profiles
    res = supabase.table("profile_groups")\
        .select("profile_id, profiles(id, name, email)")\
        .eq("group_id", group_id)\
        .execute()
    
    members = []
    for row in res.data:
        if row.get("profiles"):
            members.append(row["profiles"])
            
    return {"status": "success", "data": members}

@app.post("/api/admin/groups/{group_id}/members")
async def add_group_member(group_id: str, body: GroupMemberAction, request: Request):
    await get_current_admin(request)
    
    # 1. Find profile by email
    # Case insensitive search might be better
    profile_res = supabase.table("profiles").select("id").ilike("email", body.email).maybe_single().execute()
    
    if not profile_res.data:
        raise HTTPException(status_code=404, detail=f"User with email {body.email} not found.")
    
    profile_id = profile_res.data["id"]
    
    # 2. Insert into profile_groups
    try:
        supabase.table("profile_groups").insert({
            "profile_id": profile_id,
            "group_id": group_id
        }).execute()
    except Exception as e:
        if "unique violation" in str(e).lower() or "duplicate key" in str(e).lower():
            return {"status": "success", "message": "User already in group"}
        raise HTTPException(status_code=400, detail=str(e))
        
    return {"status": "success", "message": "Member added"}

@app.delete("/api/admin/groups/{group_id}/members/{profile_id}")
async def remove_group_member(group_id: str, profile_id: str, request: Request):
    await get_current_admin(request)
    
    supabase.table("profile_groups")\
        .delete()\
        .eq("group_id", group_id)\
        .eq("profile_id", profile_id)\
        .execute()
        
    return {"status": "success", "message": "Member removed"}

@app.get("/api/admin/profiles")
async def list_profiles(request: Request):
    await get_current_admin(request)
    res = supabase.table("profiles").select("id, name, email").order("name").execute()
    return {"status": "success", "data": res.data}

@app.get("/api/admin/profiles/{profile_id}")
async def get_profile(profile_id: str, request: Request):
    await get_current_admin(request)
    # Join with groups
    res = supabase.table("profiles")\
        .select("id, name, email, profile_groups(group_id)")\
        .eq("id", profile_id)\
        .maybe_single()\
        .execute()
    
    if not res.data:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    # Flatten group IDs
    data = res.data
    data["group_ids"] = [pg["group_id"] for pg in data.get("profile_groups", [])]
    if "profile_groups" in data: del data["profile_groups"]
    
    return {"status": "success", "data": data}

@app.post("/api/admin/profiles/{profile_id}/groups")
async def update_profile_groups(profile_id: str, body: UserGroupsUpdate, request: Request):
    await get_current_admin(request)
    
    # Simple sync: Delete all then insert new
    # Better to do in a transaction if possible, but this works for MVP
    try:
        # 1. Delete existing
        supabase.table("profile_groups").delete().eq("profile_id", profile_id).execute()
        
        # 2. Insert new
        if body.group_ids:
            inserts = [{"profile_id": profile_id, "group_id": gid} for gid in body.group_ids]
            supabase.table("profile_groups").insert(inserts).execute()
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    return {"status": "success", "message": "Groups updated successfully"}

@app.post("/api/admin/groups/{group_id}/members/batch")
async def add_group_members_batch(group_id: str, body: GroupMembersAction, request: Request):
    await get_current_admin(request)
    
    if not body.profile_ids:
        return {"status": "success", "message": "No members to add"}

    inserts = [{"profile_id": pid, "group_id": group_id} for pid in body.profile_ids]
    
    try:
        # We use a trick to avoid duplicates if possible, or just catch it.
        # Supabase doesn't easily support UPSERT via the client with specific ON CONFLICT for join tables without a unique constraint name.
        # But we'll just try and see.
        supabase.table("profile_groups").insert(inserts).execute()
    except Exception as e:
        if "unique violation" in str(e).lower() or "duplicate key" in str(e).lower():
            # If some were already there, we might still want to know.
            # But usually it's fine.
            return {"status": "success", "message": "Members added (some might have been already present)"}
        raise HTTPException(status_code=400, detail=str(e))
        
    return {"status": "success", "message": f"{len(inserts)} members added"}

@app.post("/api/admin/requests/update")
async def update_request(body: RegistrationUpdate, request: Request):
    admin = await get_current_admin(request)
    
    # 1. Update Request Status
    # Map 'DECLINED_SILENT' -> 'DECLINED', 'DECLINED_MESSAGE' -> 'DECLINED'
    # The frontend might send specific actions, but DB status is finite.
    db_status = body.action
    if body.action in ['DECLINED_SILENT', 'DECLINED_MESSAGE']:
        db_status = 'DECLINED'
    
    update_payload = {
        "status": db_status, 
        "admin_notes": body.note
    }
    
    try:
        # Fetch original request to get email and current status
        original = supabase.table("registration_requests").select("*").eq("id", body.request_id).single().execute()
        if not original.data:
             raise HTTPException(status_code=404, detail="Request not found")
        
        user_email = original.data['email']
        previous_status = original.data['status']

        # Handle revocation/reset: if it WAS approved and now it is NOT
        if previous_status == 'APPROVED' and db_status != 'APPROVED':
            # 1. Gather all possible Auth IDs for this user
            auth_ids_to_delete = set()
            
            # Check Profile
            profile_res = supabase.table("profiles").select("auth_user_id").eq("email", user_email).maybe_single().execute()
            if profile_res.data and profile_res.data.get('auth_user_id'):
                auth_ids_to_delete.add(profile_res.data['auth_user_id'])
            
            # Check Auth system directly by email (Source of Truth)
            try:
                all_users = supabase.auth.admin.list_users()
                for u in all_users:
                    if u.email.lower() == user_email.lower():
                        auth_ids_to_delete.add(u.id)
            except Exception as list_e:
                print(f"Warning: Failed to search Auth users by email {user_email}: {list_e}")

            # 2. Delete Profile
            supabase.table("profiles").delete().eq("email", user_email).execute()

            # 3. Cleanup Auth Users
            for auth_id in auth_ids_to_delete:
                try:
                    supabase.auth.admin.delete_user(auth_id)
                    print(f"Successfully deleted auth user {auth_id} for {user_email}")
                except Exception as e:
                    # We expect this might fail if one method found a stale ID
                    print(f"Note: Cleanup of auth user {auth_id} for {user_email}: {e}")

        res = supabase.table("registration_requests").update(update_payload).eq("id", body.request_id).execute()
        
        # 2. Handle Actions & Emails
        from email_service import email_service
        
        if body.action == 'APPROVED':
            # Create Profile immediately (Pre-provision)
            # Check if profiles table has this email
            profile_res = supabase.table("profiles").select("id").eq("email", user_email).execute()
            
            profile_id = None
            if profile_res.data:
                profile_id = profile_res.data[0]['id']
            else:
                # Create new profile
                new_profile = {
                    "email": user_email,
                    "name": original.data.get('full_name') or 'User'
                }
                # Auth ID is null initially
                create_res = supabase.table("profiles").insert(new_profile).execute()
                if create_res.data:
                    profile_id = create_res.data[0]['id']
            
            if profile_id:
                # Assign Groups
                # body.groups is expected to be a list of strings
                if body.groups:
                    # Resolve group names to IDs
                    # Optimization: fetch all groups once map them (or cache them)
                    all_groups = supabase.table("user_groups").select("id, name").execute()
                    group_map = {g['name']: g['id'] for g in all_groups.data}
                    
                    group_inserts = []
                    for g_name in body.groups:
                        if g_name in group_map:
                            group_inserts.append({
                                "profile_id": profile_id,
                                "group_id": group_map[g_name]
                            })
                    
                    if group_inserts:
                        # Clear existing for this profile to handle updates (Set behavior)
                        supabase.table("profile_groups").delete().eq("profile_id", profile_id).execute()
                        supabase.table("profile_groups").insert(group_inserts).execute()

            # Send Access Granted Email
            email_service.send_access_granted(user_email, original.data.get('full_name', 'User'))
            
        elif body.action == 'DECLINED_MESSAGE':
            if body.message:
                email_service.send_rejection_reason(user_email, body.message)
                
        elif body.action == 'INFO_NEEDED':
            if body.message:
                email_service.send_more_info_request(user_email, body.message)
        
        return {"status": "success", "message": f"Request marked as {db_status}", "data": res.data}
        
    except Exception as e:
        print(f"Error updating request: {e}")
        raise HTTPException(status_code=400, detail="Failed to update request")

@app.get("/api/admin/event_types")
async def list_event_types(request: Request):
    """
    Fetch all event types with user group names for admin management.
    """
    await get_current_admin(request)
    
    # Join with user_groups for all three group references
    res = supabase.table("event_types").select("""
        *,
        roster_user_group:user_groups!event_types_roster_user_group_fkey(id, name),
        reserve_first_priority_user_group:user_groups!event_types_reserve_first_priority_user_group_fkey(id, name),
        reserve_second_priority_user_group:user_groups!event_types_reserve_second_priority_user_group_fkey(id, name)
    """).order("name").execute()
    
    # Flatten the joined data for easier frontend consumption
    data = []
    for row in res.data:
        event_type = {
            "id": row["id"],
            "name": row["name"],
            "day_of_week": row["day_of_week"],
            "time_of_day": row["time_of_day"],
            "time_zone": row["time_zone"],
            "max_signups": row["max_signups"],
            "roster_sign_up_open_minutes": row["roster_sign_up_open_minutes"],
            "reserve_sign_up_open_minutes": row["reserve_sign_up_open_minutes"],
            "initial_reserve_scheduling_minutes": row["initial_reserve_scheduling_minutes"],
            "final_reserve_scheduling_minutes": row["final_reserve_scheduling_minutes"],
            "roster_user_group_id": row.get("roster_user_group", {}).get("id") if row.get("roster_user_group") else None,
            "roster_user_group_name": row.get("roster_user_group", {}).get("name") if row.get("roster_user_group") else None,
            "reserve_first_priority_user_group_id": row.get("reserve_first_priority_user_group", {}).get("id") if row.get("reserve_first_priority_user_group") else None,
            "reserve_first_priority_user_group_name": row.get("reserve_first_priority_user_group", {}).get("name") if row.get("reserve_first_priority_user_group") else None,
            "reserve_second_priority_user_group_id": row.get("reserve_second_priority_user_group", {}).get("id") if row.get("reserve_second_priority_user_group") else None,
            "reserve_second_priority_user_group_name": row.get("reserve_second_priority_user_group", {}).get("name") if row.get("reserve_second_priority_user_group") else None,
        }
        data.append(event_type)
    
    return {"status": "success", "data": data}

@app.post("/api/admin/event_types")
async def create_event_type(body: EventTypeCreate, request: Request):
    """
    Create a new event type.
    """
    await get_current_admin(request)
    
    try:
        payload = body.model_dump()
        res = supabase.table("event_types").insert(payload).execute()
        
        if not res.data:
            raise HTTPException(status_code=500, detail="Failed to create event type")
        
        return {"status": "success", "message": "Event type created", "data": res.data[0]}
    except Exception as e:
        print(f"Error creating event type: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to create event type: {str(e)}")

@app.put("/api/admin/event_types/{event_type_id}")
async def update_event_type(event_type_id: str, body: EventTypeUpdate, request: Request):
    """
    Update an existing event type. Only updates fields that are provided.
    """
    await get_current_admin(request)
    
    try:
        # Only include fields that were actually provided
        payload = body.model_dump(exclude_unset=True)
        
        if not payload:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        res = supabase.table("event_types").update(payload).eq("id", event_type_id).execute()
        
        if not res.data:
            raise HTTPException(status_code=404, detail="Event type not found")
        
        return {"status": "success", "message": "Event type updated", "data": res.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating event type: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to update event type: {str(e)}")

@app.delete("/api/admin/event_types/{event_type_id}")
async def delete_event_type(event_type_id: str, request: Request):
    """
    Delete an event type. This will cascade to related events.
    """
    await get_current_admin(request)
    
    try:
        res = supabase.table("event_types").delete().eq("id", event_type_id).execute()
        
        # Supabase delete doesn't error if nothing was deleted, so check data
        if not res.data:
            raise HTTPException(status_code=404, detail="Event type not found")
        
        return {"status": "success", "message": "Event type deleted"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting event type: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to delete event type: {str(e)}")

@app.post("/api/signup")
async def signup(body: SignupRequest, request: Request):
    # 0. Verify Auth
    # Retrieve user from token to ensure they are who they say they are
    auth_user = await get_current_user(request)
    
    # 1. Fetch Event & User
    user_id = body.user_id 
    
    # Security Check: Enforce that the token's user_id matches the requested user_id
    # (Unless we want admins to sign up others, but for now strict self-signup)
    if auth_user.id != user_id:
        raise HTTPException(status_code=403, detail="You can only sign up yourself.")

    print(f"Signup Request: user={user_id} event={body.event_id}")
    try:
        event = fetch_event(body.event_id)
    except Exception as e:
        print(f"Error fetching event: {e}")
        raise HTTPException(status_code=404, detail="Event not found")

    # Check if already signed up
    # existing = supabase.table("event_signups").select("*").eq("event_id", body.event_id).eq("user_id", user_id).execute()
    # if existing.data:
    #     raise HTTPException(status_code=400, detail="User already signed up")
    
    try:
        # Fetch profile with groups (via join table)
        profile_res = supabase.table("profiles").select("*, profile_groups(user_groups(id, name))").eq("auth_user_id", user_id).execute()
        
        profile = None
        if not profile_res.data:
            # Attempt to create profile if missing (Self-healing)
            print(f"Profile not found for {user_id}. Attempting to create with Service Role...")
            try:
                # We utilize the 'supabase' client which should now have SERVICE ROLE capabilities from db.py
                new_profile = {
                    "id": user_id,
                    "auth_user_id": user_id,  # Link to auth user
                    "email": auth_user.email  # Required for pre-provisioning schema
                }
                
                # Attempt to get name from metadata
                meta = auth_user.user_metadata or {}
                if "full_name" in meta:
                    new_profile["name"] = meta["full_name"]
                
                create_res = supabase.table("profiles").insert(new_profile).execute()
                profile = create_res.data[0]
                # Refetch with groups (will be empty)
                profile["profile_groups"] = []
                print(f"Successfully auto-created profile for {user_id}")
            except Exception as create_e:
                print(f"Failed to auto-create profile: {create_e}")
                # Check if it was an RLS error (which means we still don't have Service Key)
                if "policy" in str(create_e):
                    print("CRITICAL: RLS Error. SUPABASE_SERVICE_ROLE_KEY is likely missing or invalid in server environment.")
                
                raise HTTPException(status_code=400, detail="User profile not found and could not be created. Please contact support.")
        else:
            profile = profile_res.data[0]
            
    except Exception as e:
        print(f"Error fetching/creating profile: {e}")
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Database error checking profile: {str(e)}")

    # Check if already signed up (using Profile ID)
    existing = supabase.table("event_signups").select("*").eq("event_id", body.event_id).eq("user_id", profile["id"]).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="User already signed up")

    # Flatten groups
    user_groups = []
    user_group_ids = []
    if profile.get("profile_groups"):
        for pg in profile["profile_groups"]:
            if pg.get("user_groups"):
                group_data = pg["user_groups"]
                if group_data.get("name"):
                    user_groups.append(group_data["name"])
                if group_data.get("id"):
                    user_group_ids.append(group_data["id"])

    # Determine Access
    is_member = len(user_groups) > 0 or len(user_group_ids) > 0
    
    if not is_member:
        # If user has NO groups, they cannot sign up.
        raise HTTPException(status_code=403, detail="Only approved members can sign up for events.")

    # 2. Logic
    try:
        now = get_now()
        
        # Check Eligibility
        eligibility = check_signup_eligibility(event, user_group_ids, now)
        
        if not eligibility["allowed"]:
             raise HTTPException(status_code=400, detail=eligibility["error_message"])
             
        target_list = eligibility["target_list"]
        
        # If target is EVENT, we still need to check if it's full (Overflow to WAITLIST)
        # But if target is WAITLIST_HOLDING, we just put them there.
        
        sequence = 0
        final_list_type = target_list
        
        if target_list == "EVENT":
            # Check capacity
            roster_count = fetch_counts(body.event_id)
            max_signups = event['max_signups']
            
            if roster_count < max_signups:
                final_list_type = "EVENT"
                sequence = roster_count + 1
            else:
                final_list_type = "WAITLIST"
                # Get waitlist count
                wl_res = supabase.table("event_signups").select("id", count="exact").eq("event_id", body.event_id).eq("list_type", "WAITLIST").execute()
                sequence = (wl_res.count or 0) + 1
        elif target_list == "WAITLIST_HOLDING":
            final_list_type = "WAITLIST_HOLDING"
            # Sequence for holding can heavily rely on created_at, but we can store an incrementing seq too if we want.
            # logic.py sorts by created_at for window 2. 
            # Let's just set sequence to 0 or something for now, or use max + 1 if we want to track insertion order explicitly.
            final_list_type = "WAITLIST_HOLDING"
            seq_res = supabase.table("event_signups").select("id", count="exact").eq("event_id", body.event_id).eq("list_type", "WAITLIST_HOLDING").execute()
            sequence = (seq_res.count or 0) + 1

        # 3. Execute Insert
        payload = {
            "event_id": body.event_id,
            "user_id": profile["id"],
            "list_type": final_list_type,
            "sequence_number": sequence,
            "tier": eligibility.get("tier") # Store tier for sorting later
        }
        
        print(f"DEBUG: Payload for insert: {payload}")
        res = supabase.table("event_signups").insert(payload).execute()
        
        if not res.data:
            print(f"DEBUG: Insert returned no data. res={res}")
            raise HTTPException(status_code=500, detail="Failed to insert signup record")

        return {"status": "success", "data": res.data[0]}
    except Exception as e:
        print(f"DEBUG: Signup Error: {e}")
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Internal Logic Error: {str(e)}")


@app.post("/api/remove-signup")
async def remove_signup(body: SignupRequest, request: Request):
    auth_user = await get_current_user(request)
    
    if auth_user.id != body.user_id:
        raise HTTPException(status_code=403, detail="You can only remove yourself.")
    
    try:
        # Get profile ID first
        profile_res = supabase.table("profiles").select("id").eq("auth_user_id", auth_user.id).single().execute()
        if not profile_res.data:
             raise HTTPException(status_code=404, detail="Profile not found")
        
        target_profile_id = profile_res.data["id"]

        # 1. Fetch current signup status BEFORE deleting
        current_signup_res = supabase.table("event_signups")\
            .select("list_type")\
            .eq("event_id", body.event_id)\
            .eq("user_id", target_profile_id)\
            .maybe_single()\
            .execute()
            
        current_list_type = current_signup_res.data["list_type"] if current_signup_res.data else None

        # 2. Delete the signup
        res = supabase.table("event_signups").delete().eq("event_id", body.event_id).eq("user_id", target_profile_id).execute()
        
        # 3. Auto-Promote if needed
        # If the user was in the EVENT list, we should promote the first person from WAITLIST.
        # We explicitly IGNORE "WAITLIST_HOLDING" - they are not ready for promotion yet.
        if current_list_type == "EVENT":
            print(f"User removed from EVENT roster. checking for waitlist promotion...")
            
            # Find the highest priority waitlist member
            # Sorted by sequence_number ascending (1, 2, 3...)
            # If sequence is null/zero, fall back to created_at
            next_up_res = supabase.table("event_signups")\
                .select("*")\
                .eq("event_id", body.event_id)\
                .eq("list_type", "WAITLIST")\
                .order("sequence_number", desc=False)\
                .order("created_at", desc=False)\
                .limit(1)\
                .execute()
                
            if next_up_res.data:
                next_person = next_up_res.data[0]
                print(f"Promoting user {next_person['user_id']} from WAITLIST to EVENT")
                
                # Get current max sequence for EVENT? Or just append?
                # Actually, sequence in EVENT list matters less for order, but let's be tidy.
                # Just appending is fine.
                
                # Update them to EVENT
                supabase.table("event_signups").update({
                    "list_type": "EVENT"
                }).eq("id", next_person["id"]).execute()
                
                # Notification logic would go here (Notify promoted user)

        return {"status": "success", "message": "Signup removed"}
    except Exception as e:
        print(f"Error removing signup: {e}")
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail="Failed to remove signup")


@app.get("/api/events")
async def get_events(request: Request):
    # Authenticated endpoint to list upcoming events
    await get_current_user(request)
    
    # 1. Fetch events + types
    # Filter: event_date >= now (or maybe slightly in past?)
    # User said "list of upcoming events".
    now = get_now()
    
    events_res = supabase.table("events")\
        .select("*, event_types(*)")\
        .gte("event_date", now.isoformat())\
        .order("event_date")\
        .execute()
        
    enriched_events = [enrich_event(e) for e in events_res.data]
    
    # 2. Fetch counts
    event_ids = [e['id'] for e in enriched_events]
    
    if not event_ids:
         return enriched_events
         
    # Fetch all signups for these events
    signups_res = supabase.table("event_signups")\
        .select("event_id, list_type")\
        .in_("event_id", event_ids)\
        .execute()
        
    # Aggregate
    counts_map = {eid: {"roster": 0, "waitlist": 0, "holding": 0} for eid in event_ids}
    
    for s in signups_res.data:
        eid = s['event_id']
        ltype = s['list_type']
        if eid in counts_map:
            if ltype == "EVENT":
                counts_map[eid]["roster"] += 1
            elif ltype == "WAITLIST":
                counts_map[eid]["waitlist"] += 1
            elif ltype == "WAITLIST_HOLDING":
                counts_map[eid]["holding"] += 1
                
    # Attach
    for e in enriched_events:
        e['counts'] = counts_map.get(e['id'], {"roster": 0, "waitlist": 0, "holding": 0})
    
    return enriched_events


@app.post("/api/schedule")
async def trigger_schedule(request: Request):
    """
    Auto-schedule guests from Holding Area -> Event/Waitlist
    Run this periodically or trigger manually.
    """
    # Security Check
    expected_secret = os.environ.get("CRON_SECRET")
    if not expected_secret:
        print("WARNING: CRON_SECRET not set in environment. Endpoint is insecure.")
    
    # Check header
    # Cloud Scheduler sends these headers
    cron_header = request.headers.get("X-Cron-Secret")
    
    if expected_secret and cron_header != expected_secret:
        print(f"Unauthorized schedule attempt. Header: {cron_header}")
        raise HTTPException(status_code=401, detail="Unauthorized")

    now = get_now()
    
    # --- STATUS UPDATE ROUTINE ---
    # Fetch all events that are NOT Finished or Cancelled
    
    active_events_res = supabase.table("events")\
        .select("*, event_types(*)")\
        .neq("status", "FINISHED")\
        .neq("status", "CANCELLED")\
        .execute()
        
    enriched_active = [enrich_event(e) for e in active_events_res.data]
    
    from logic import determine_event_status
    
    processed_count = 0
    promoted_count = 0
    
    for event in enriched_active:
        current_status = event["status"]
        
        # Calculate what status SHOULD be based on time
        # enrich_event no longer auto-sets this for us (except for legacy SCHEDULED)
        # So we must calculate it here explicitly to drive the state machine.
        target_status = determine_event_status(event, now)
        
        # Check for Manual Override
        # If status_determinant is MANUAL, we do NOT auto-update the status based on time.
        # We only respect the current status (which is what we started with).
        if event.get("status_determinant") == "MANUAL":
            # However, we MIGHT still need to process Holding Queue if it was manually set to FINAL_ORDERING?
            # actually logic says: if target == FINAL and current != FINAL -> process.
            # But if manual, target IS current (effectively).
            # So if it IS ALREADY FINAL_ORDERING, we might need to process holding? 
            # The Cron job is "state change" driven mostly.
            # But if admin manually sets to FINAL_ORDERING, the cron might pick it up?
            # If admin sets it, they hopefully trigger the RPC or we rely on this script to see "Oh it is FINAL_ORDERING"
            # But wait, if it IS FINAL_ORDERING, does it need processing?
            # The transition logic handles "entering" the state.
            # If manual, we don't "transition" automatically.
            # So we force target to be current, so no transition happens.
            target_status = current_status
        
        if target_status == current_status:
            continue
            
        print(f"Event {event['id']}: Transitioning {current_status} -> {target_status}")
        
        # TRANSACTIONAL SAFETY LOGIC:
        # If we are transitioning to FINAL_ORDERING, we must process the Holding Queue FIRST.
        # This ensures that if the process fails mid-way, the status remains in the old state (e.g. PRELIMINARY_ORDERING).
        # The next Cron run will see the old state + current time and try again.
        
        if target_status == "PRELIMINARY_ORDERING" and current_status != "PRELIMINARY_ORDERING":
            # 1. Enter Preliminary Ordering: Randomize Holding Queue & Assign Sequence
            print(f"Entering Preliminary Ordering for Event {event['id']}: Randomizing Holding Queue...")
            
            holding_res = supabase.table("event_signups")\
                .select("*")\
                .eq("event_id", event["id"])\
                .eq("list_type", "WAITLIST_HOLDING")\
                .execute()
                
            holding_users = holding_res.data
            
            if holding_users:
                # A. Randomize (Tier 2/3 logic)
                queue = randomize_holding_queue(holding_users)
                
                # B. Assign Sequence Numbers (But keep in WAITLIST_HOLDING)
                updates = resequence_holding(queue)
                
                 # C. Execute Moves (Atomic Batch via RPC)
                update_list = []
                for update in updates:
                    update_list.append({
                        "id": str(update["id"]),
                        "list_type": update["list_type"],
                        "sequence_number": update["sequence_number"]
                    })
                
                print(f"Executing RPC for Preliminary Randomization ({len(update_list)} updates)...")
                
                try:
                    rpc_res = supabase.rpc("update_event_status_batch", {
                        "p_event_id": str(event["id"]),
                        "p_updates": update_list,
                        "p_final_status": target_status
                    }).execute()
                    
                    print(f"RPC Result: {rpc_res.data}")
                    processed_count += 1
                    
                except Exception as rpc_e:
                    print(f"CRITICAL: RPC Failed for Event {event['id']}: {rpc_e}")
                    continue
            else:
                 # No one in holding? Just update status.
                 try:
                    supabase.rpc("update_event_status_batch", {
                        "p_event_id": str(event["id"]),
                        "p_updates": [],
                        "p_final_status": target_status
                    }).execute()
                    processed_count += 1
                 except Exception as e:
                    print(f"Error updating status to PRELIMINARY for {event['id']}: {e}")

        elif target_status == "FINAL_ORDERING" and current_status != "FINAL_ORDERING":
            # 2. Enter Final Ordering: Lock in placements
            # FETCH ORDERED BY SEQUENCE (Respecting the Preliminary Randomization)
            print(f"Entering Final Ordering for Event {event['id']}: Promoting from Holding...")
            
            holding_res = supabase.table("event_signups")\
                .select("*")\
                .eq("event_id", event["id"])\
                .eq("list_type", "WAITLIST_HOLDING")\
                .order("sequence_number", desc=False)\
                .execute()
                
            holding_users = holding_res.data
            
            if holding_users:
                # Do NOT randomize again. Used established order.
                queue = holding_users
                
                # B. Get current counts
                roster_res = supabase.table("event_signups").select("id", count="exact").eq("event_id", event["id"]).eq("list_type", "EVENT").execute()
                current_roster_count = roster_res.count or 0
                
                waitlist_res = supabase.table("event_signups").select("id", count="exact").eq("event_id", event["id"]).eq("list_type", "WAITLIST").execute()
                current_waitlist_count = waitlist_res.count or 0
                
                # C. Calculate Moves
                updates = promote_from_holding(queue, current_roster_count, event["max_signups"], current_waitlist_count)
                
                # D. Execute Moves (Atomic Batch via RPC)
                update_list = []
                for update in updates:
                    update_list.append({
                        "id": str(update["id"]),
                        "list_type": update["list_type"],
                        "sequence_number": update["sequence_number"]
                    })
                
                print(f"Executing RPC for Final Promotion ({len(update_list)} updates)...")
                
                try:
                    rpc_res = supabase.rpc("update_event_status_batch", {
                        "p_event_id": str(event["id"]),
                        "p_updates": update_list,
                        "p_final_status": target_status
                    }).execute()
                    
                    print(f"RPC Result: {rpc_res.data}")
                    processed_count += 1
                    promoted_count += len(update_list)
                    
                except Exception as rpc_e:
                    print(f"CRITICAL: RPC Failed for Event {event['id']}: {rpc_e}")
                    continue
            else:
                 # No one in holding? Just update status.
                 try:
                    supabase.rpc("update_event_status_batch", {
                        "p_event_id": str(event["id"]),
                        "p_updates": [],
                        "p_final_status": target_status
                    }).execute()
                    processed_count += 1
                 except Exception as e:
                    print(f"Error updating status to FINAL for {event['id']}: {e}")

        else:
            # 3. Simple Transition (e.g. NOT_YET_OPEN -> OPEN_FOR_ROSTER)
            # Use RPC ensuring it is transactional even if just one update
            print(f"Executing RPC update_event_status_batch (Status Only update)...")
            try:
                supabase.rpc("update_event_status_batch", {
                    "p_event_id": str(event["id"]),
                    "p_updates": [], # Empty list
                    "p_final_status": target_status
                }).execute()
                processed_count += 1
            except Exception as e:
                print(f"Error updating status for {event['id']}: {e}")

    return {"status": "completed", "processed_events": processed_count, "users_promoted": promoted_count}



# Serve React App (SPA)
app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    from fastapi.responses import Response
    
    file_path = f"static/{full_path}"
    if os.path.isfile(file_path):
        # For HTML files, disable caching to ensure fresh content
        if file_path.endswith('.html'):
            with open(file_path, 'r') as f:
                content = f.read()
            return Response(
                content=content,
                media_type="text/html",
                headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0"
                }
            )
        return FileResponse(file_path)
    
    # Serve index.html for client-side routing with no-cache headers
    with open("static/index.html", 'r') as f:
        content = f.read()
    return Response(
        content=content,
        media_type="text/html",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )
