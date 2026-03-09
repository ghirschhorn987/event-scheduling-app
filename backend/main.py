import os
import random
from datetime import datetime, timezone
from typing import List, Optional
import pytz

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from db import supabase
from models import (
    SignupRequest, ScheduleResponse, RegistrationRequest, RegistrationUpdate,
    GroupMemberAction, GroupMembersAction, UserGroupsUpdate, UserGroupMetadataUpdate,
    EventTypeCreate, EventTypeUpdate, EventStatusUpdate, CancelledDate, BulkUserCreate
)
from mock_google_service import sync_to_google
from logic import enrich_event, randomize_holding_queue, promote_from_holding, check_signup_eligibility, determine_event_status, resequence_holding, parse_interval_to_minutes, generate_future_events
from email_service import email_service

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
            "group_email": row.get("group_email"),
            "guest_limit": row.get("guest_limit", 0),
            "group_type": row.get("group_type", "OTHER"),
            "user_count": count
        })
    return {"status": "success", "data": data}

@app.put("/api/admin/groups/{group_id}")
async def update_user_group(group_id: str, body: UserGroupMetadataUpdate, request: Request):
    """
    Update group metadata (name, description, google_group_id, group_email).
    """
    user = await get_current_admin(request)
    
    update_data = {}
    if body.name is not None: update_data["name"] = body.name
    if body.description is not None: update_data["description"] = body.description
    if body.google_group_id is not None: update_data["google_group_id"] = body.google_group_id
    if body.group_email is not None: update_data["group_email"] = body.group_email
    if body.guest_limit is not None: update_data["guest_limit"] = body.guest_limit
    if body.group_type is not None: update_data["group_type"] = body.group_type

    if not update_data:
        return {"status": "success", "message": "No fields to update"}

    try:
        res = supabase.table("user_groups")\
            .update(update_data)\
            .eq("id", group_id)\
            .execute()
        
        if not res.data:
            raise HTTPException(status_code=404, detail="Group not found")
            
        return {"status": "success", "data": res.data[0]}
    except Exception as e:
        print(f"Error updating user group: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/groups/{group_id}/sync")
async def trigger_group_sync(group_id: str, request: Request):
    """
    Trigger a sync of Supabase group members to Google Groups (Mocked).
    """
    await get_current_admin(request)
    
    res = await sync_to_google(group_id)
    if res.get("status") == "error":
        raise HTTPException(status_code=500, detail=res.get("message"))
        
    return res

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

@app.post("/api/admin/users/bulk-pre-approve")
async def bulk_pre_approve_users(body: List[BulkUserCreate], request: Request):
    admin = await get_current_admin(request)
    
    # 1. Map all group names to IDs
    all_groups_res = supabase.table("user_groups").select("id, name").execute()
    group_map = {g['name']: g['id'] for g in all_groups_res.data}
    
    success_count = 0
    errors = []
    
    from email_service import email_service
    
    for user_data in body:
        try:
            user_email = user_data.email.strip().lower()
            
            # Check if profile already exists
            profile_res = supabase.table("profiles").select("id").eq("email", user_email).execute()
            
            profile_id = None
            if profile_res.data:
                profile_id = profile_res.data[0]['id']
            else:
                # Create profile
                new_profile = {
                    "email": user_email,
                    "name": user_data.full_name.strip() or 'User'
                }
                create_res = supabase.table("profiles").insert(new_profile).execute()
                if create_res.data:
                    profile_id = create_res.data[0]['id']
            
            if profile_id:
                # Assign groups
                if user_data.groups:
                    group_inserts = []
                    for g_name in user_data.groups:
                        cl_name = g_name.strip()
                        if cl_name in group_map:
                            group_inserts.append({
                                "profile_id": profile_id,
                                "group_id": group_map[cl_name]
                            })
                    
                    if group_inserts:
                        # Clear and re-add groups to be safe without duplicating
                        supabase.table("profile_groups").delete().eq("profile_id", profile_id).execute()
                        supabase.table("profile_groups").insert(group_inserts).execute()
                        
                # Create a Registration Request record for history purposes
                req_payload = {
                    "email": user_email,
                    "full_name": user_data.full_name.strip() or 'User',
                    "affiliation": "Bulk Import",
                    "status": "APPROVED",
                    "admin_notes": "Added via CSV Bulk Import"
                }
                supabase.table("registration_requests").insert(req_payload).execute()

                # Send Email
                try:
                    email_service.send_access_granted(user_email, user_data.full_name.strip() or 'User')
                except Exception as e:
                    print(f"Failed to send email to {user_email}: {e}")
                    
                success_count += 1
                
        except Exception as err:
            errors.append(f"Failed for {user_data.email}: {str(err)}")
            
    return {"status": "success", "success_count": success_count, "errors": errors}

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
            "duration_minutes": parse_interval_to_minutes(row.get("duration"))
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
        # Convert duration_minutes to Postgres Interval string
        if "duration_minutes" in payload:
            payload["duration"] = f"{payload['duration_minutes']} minutes"
            del payload["duration_minutes"]
            
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

        # Convert duration_minutes to Postgres Interval string
        if "duration_minutes" in payload:
             payload["duration"] = f"{payload['duration_minutes']} minutes"
             del payload["duration_minutes"]
        
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

# --- New Admin Event Management Endpoints ---

@app.get("/api/admin/events")
async def list_admin_events(request: Request, filter: str = "future"):
    """
    Fetch all events for admin management (including cancelled/finished).
    """
    await get_current_admin(request)
    
    try:
        query = supabase.table("events").select("*, event_types(name)")
        now = get_now()
        
        if filter == "future":
            query = query.gte("event_date", now.isoformat())
            query = query.order("event_date", desc=False)
        elif filter == "past":
            query = query.lt("event_date", now.isoformat())
            query = query.order("event_date", desc=True)
        else:
            query = query.order("event_date", desc=False)
            
        res = query.limit(200).execute()
        
        # Fetch counts (Item 5)
        event_ids = [row["id"] for row in res.data]
        counts_map = {eid: {"roster": 0, "waitlist_holding": 0} for eid in event_ids}
        
        if event_ids:
            signups_res = supabase.table("event_signups")\
                .select("event_id, list_type")\
                .in_("event_id", event_ids)\
                .execute()
                
            for s in signups_res.data:
                eid = s['event_id']
                ltype = s['list_type']
                if eid in counts_map:
                    if ltype == "EVENT":
                        counts_map[eid]["roster"] += 1
                    elif ltype in ["WAITLIST", "WAITLIST_HOLDING"]:
                        counts_map[eid]["waitlist_holding"] += 1
        
        data = []
        for row in res.data:
            event = {
                "id": row["id"],
                "event_type_id": row["event_type_id"],
                "event_type_name": row.get("event_types", {}).get("name") if row.get("event_types") else "Unknown",
                "event_date": row["event_date"],
                "status": row["status"],
                "status_determinant": row.get("status_determinant", "AUTOMATIC"),
                "duration": row.get("duration"),
                "counts": counts_map.get(row["id"], {"roster": 0, "waitlist_holding": 0})
            }
            data.append(event)
            
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"Error listing admin events: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to list events: {e}")

from models import EventStatusUpdate

@app.put("/api/admin/events/{event_id}/status")
async def update_event_status(event_id: str, body: EventStatusUpdate, request: Request):
    """
    Manually update event status and determinant.
    """
    await get_current_admin(request)
    
    try:
        payload = {
            "status": body.status,
            "status_determinant": body.status_determinant
        }
        
        res = supabase.table("events").update(payload).eq("id", event_id).execute()
        
        if not res.data:
            raise HTTPException(status_code=404, detail="Event not found")
            
        return {"status": "success", "message": "Event status updated", "data": res.data[0]}
    except Exception as e:
        print(f"Error updating event status: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to update status: {e}")

@app.get("/api/admin/cancelled_dates")
async def list_cancelled_dates(request: Request):
    """
    List all future cancelled dates.
    """
    await get_current_admin(request)
    
    try:
        # Fetch dates >= today
        today = datetime.now().strftime("%Y-%m-%d")
        res = supabase.table("cancelled_dates").select("*").gte("date", today).order("date").execute()
        return {"status": "success", "data": res.data}
    except Exception as e:
        print(f"Error fetching cancelled dates: {e}")
        # Identify if table exists error? For now just 500
        raise HTTPException(status_code=500, detail=f"Failed to fetch cancelled dates: {e}")

from models import CancelledDate

@app.post("/api/admin/cancelled_dates")
async def add_cancelled_date(body: CancelledDate, request: Request):
    """
    Add a date to the blocklist.
    """
    await get_current_admin(request)
    
    try:
        payload = {
            "date": body.date,
            "reason": body.reason
        }
        res = supabase.table("cancelled_dates").insert(payload).execute()
        return {"status": "success", "data": res.data[0]}
    except Exception as e:
        print(f"Error adding cancelled date: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to add date: {e}")

@app.delete("/api/admin/cancelled_dates/{date_str}")
async def remove_cancelled_date(date_str: str, request: Request):
    """
    Remove a date from the blocklist.
    """
    await get_current_admin(request)
    
    try:
        res = supabase.table("cancelled_dates").delete().eq("date", date_str).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Date not found in blocklist")
        return {"status": "success", "message": "Date removed"}
    except Exception as e:
         print(f"Error removing cancelled date: {e}")
         raise HTTPException(status_code=400, detail=f"Failed to remove date: {e}")

from models import AdminEventUserAdd, AdminEventUserReorderRequest, AdminEventUserMove

@app.get("/api/admin/events/{event_id}/users")
async def list_admin_event_users(event_id: str, request: Request):
    """
    Fetch all signups for a specific event, enriched with user profile data.
    """
    await get_current_admin(request)
    try:
        res = supabase.table("event_signups").select("*, profiles(name, email)").eq("event_id", event_id).order("sequence_number").execute()
        return {"status": "success", "data": res.data}
    except Exception as e:
        print(f"Error fetching event users: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to fetch users: {e}")

@app.post("/api/admin/events/{event_id}/users")
async def add_admin_event_user(event_id: str, body: AdminEventUserAdd, request: Request):
    """
    Add a user (by profile_id or as guest) to a specific list for an event.
    """
    await get_current_admin(request)
    try:
        # Get current max sequence for the target list
        seq_res = supabase.table("event_signups").select("id", count="exact").eq("event_id", event_id).eq("list_type", body.target_list).execute()
        sequence = (seq_res.count or 0) + 1
        
        payload = {
            "event_id": event_id,
            "list_type": body.target_list,
            "sequence_number": sequence,
            "is_guest": body.is_guest,
            "guest_name": body.guest_name
        }
        if body.profile_id:
            payload["user_id"] = body.profile_id
            
        res = supabase.table("event_signups").insert(payload).execute()
        return {"status": "success", "data": res.data[0]}
    except Exception as e:
        print(f"Error adding event user: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to add user: {e}")

@app.delete("/api/admin/events/{event_id}/users/{signup_id}")
async def remove_admin_event_user(event_id: str, signup_id: str, request: Request):
    """
    Remove a specific signup record and decrement subsequent sequence numbers.
    """
    await get_current_admin(request)
    try:
        # Fetch current to get list_type and sequence
        current_res = supabase.table("event_signups").select("*").eq("id", signup_id).maybe_single().execute()
        if not current_res.data:
            raise HTTPException(status_code=404, detail="Signup not found")
            
        current_data = current_res.data
        
        signups_to_remove_ids = [current_data["id"]]
        if not current_data.get("is_guest"):
            guests_res = supabase.table("event_signups").select("id").eq("event_id", event_id).eq("user_id", current_data["user_id"]).eq("is_guest", True).execute()
            if guests_res.data:
                signups_to_remove_ids.extend([g["id"] for g in guests_res.data])

        for s_id in signups_to_remove_ids:
            fresh_res = supabase.table("event_signups").select("*").eq("id", s_id).maybe_single().execute()
            if not fresh_res.data:
                continue

            fresh_data = fresh_res.data
            current_list = fresh_data["list_type"]
            current_seq = fresh_data["sequence_number"]
            
            # Delete
            supabase.table("event_signups").delete().eq("id", s_id).execute()
            
            # Update sequences
            to_update = supabase.table("event_signups").select("id, sequence_number").eq("event_id", event_id).eq("list_type", current_list).gt("sequence_number", current_seq).execute()
            for row in to_update.data:
                supabase.table("event_signups").update({"sequence_number": row["sequence_number"] - 1}).eq("id", row["id"]).execute()
            
        return {"status": "success", "message": "User removed from event"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error removing event user: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to remove user: {e}")

@app.put("/api/admin/events/{event_id}/users/reorder")
async def reorder_admin_event_users(event_id: str, body: AdminEventUserReorderRequest, request: Request):
    """
    Reorder users in a specific list.
    """
    await get_current_admin(request)
    try:
        # Let's do individual updates for safety
        for item in body.items:
            supabase.table("event_signups").update({"sequence_number": item.sequence_number}).eq("id", item.signup_id).execute()
            
        return {"status": "success", "message": "Users reordered"}
    except Exception as e:
        print(f"Error reordering event users: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to reorder users: {e}")

@app.put("/api/admin/events/{event_id}/users/{signup_id}/move")
async def move_admin_event_user(event_id: str, signup_id: str, body: AdminEventUserMove, request: Request):
    """
    Move a user to a different list type.
    """
    await get_current_admin(request)
    try:
        # Fetch current
        current_res = supabase.table("event_signups").select("*").eq("id", signup_id).maybe_single().execute()
        if not current_res.data:
            raise HTTPException(status_code=404, detail="Signup not found")
            
        current_data = current_res.data
        old_list = current_data["list_type"]
        old_seq = current_data["sequence_number"]
        new_list = body.target_list
        
        if old_list == new_list:
            return {"status": "success", "message": "User already in target list"}
            
        # Get max seq for new list
        seq_res = supabase.table("event_signups").select("id", count="exact").eq("event_id", event_id).eq("list_type", new_list).execute()
        new_seq = (seq_res.count or 0) + 1
        
        # Update user to new list and new seq
        supabase.table("event_signups").update({
            "list_type": new_list,
            "sequence_number": new_seq
        }).eq("id", signup_id).execute()
        
        # Decrement old list sequences
        to_update = supabase.table("event_signups").select("id, sequence_number").eq("event_id", event_id).eq("list_type", old_list).gt("sequence_number", old_seq).execute()
        for row in to_update.data:
            supabase.table("event_signups").update({"sequence_number": row["sequence_number"] - 1}).eq("id", row["id"]).execute()
            
        return {"status": "success", "message": f"User moved to {new_list}"}
    except Exception as e:
        print(f"Error moving event user: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to move user: {e}")

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
        profile_res = supabase.table("profiles").select("*, profile_groups(user_groups(id, name, guest_limit))").eq("auth_user_id", user_id).execute()
        
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
    if not body.is_guest:
        existing = supabase.table("event_signups").select("*").eq("event_id", body.event_id).eq("user_id", profile["id"]).eq("is_guest", False).execute()
        if existing.data:
            raise HTTPException(status_code=400, detail="User already signed up")

    # Flatten groups
    user_groups = []
    user_group_ids = []
    max_guest_limit = 0
    if profile.get("profile_groups"):
        for pg in profile["profile_groups"]:
            if pg.get("user_groups"):
                group_data = pg["user_groups"]
                if group_data.get("name"):
                    user_groups.append(group_data["name"])
                if group_data.get("id"):
                    user_group_ids.append(group_data["id"])
                gl = group_data.get("guest_limit")
                if gl and gl > max_guest_limit:
                    max_guest_limit = gl

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

        if body.is_guest:
            if max_guest_limit <= 0:
                raise HTTPException(status_code=403, detail="You do not have permission to add guests.")
            
            guest_count_res = supabase.table("event_signups").select("id", count="exact").eq("event_id", body.event_id).eq("user_id", profile["id"]).eq("is_guest", True).execute()
            current_guests = guest_count_res.count or 0
            if current_guests >= max_guest_limit:
                raise HTTPException(status_code=400, detail=f"You have reached your guest limit of {max_guest_limit} for this event.")
            
            if not body.guest_name:
                raise HTTPException(status_code=400, detail="Guest name is required.")
        target_list = eligibility["target_list"]
        
        sequence = 0
        final_list_type = target_list

        if body.is_guest:
            # New specific guest routing logic:
            event_status = event.get('status')
            
            if event_status in ["OPEN_FOR_ROSTER", "OPEN_FOR_RESERVES", "PRELIMINARY_ORDERING"]:
                # Guest goes to WAITLIST specifically, not EVENT/HOLDING.
                # Since we sort by sequence, we just stick them at the bottom of the Waitlist.
                # (Later, they will be processed before reserves in the scheduler, but for now they just go to WAITLIST).
                final_list_type = "WAITLIST"
                wl_res = supabase.table("event_signups").select("id", count="exact").eq("event_id", body.event_id).eq("list_type", "WAITLIST").execute()
                sequence = (wl_res.count or 0) + 1
            elif event_status == "FINAL_ORDERING":
                # Regular FCFS flow
                roster_count = fetch_counts(body.event_id)
                max_signups = event['max_signups']
                if roster_count < max_signups:
                    final_list_type = "EVENT"
                    sequence = roster_count + 1
                else:
                    final_list_type = "WAITLIST"
                    wl_res = supabase.table("event_signups").select("id", count="exact").eq("event_id", body.event_id).eq("list_type", "WAITLIST").execute()
                    sequence = (wl_res.count or 0) + 1
            else:
                # Fallback, just force to waitlist
                final_list_type = "WAITLIST"
                wl_res = supabase.table("event_signups").select("id", count="exact").eq("event_id", body.event_id).eq("list_type", "WAITLIST").execute()
                sequence = (wl_res.count or 0) + 1
            
            eligibility["tier"] = 0 # Top priority for sorting technically
        else:
            # Regular user processing
            if target_list == "EVENT":
                roster_count = fetch_counts(body.event_id)
                max_signups = event['max_signups']
                if roster_count < max_signups:
                    final_list_type = "EVENT"
                    sequence = roster_count + 1
                else:
                    final_list_type = "WAITLIST"
                    wl_res = supabase.table("event_signups").select("id", count="exact").eq("event_id", body.event_id).eq("list_type", "WAITLIST").execute()
                    sequence = (wl_res.count or 0) + 1
            elif target_list == "WAITLIST_HOLDING":
                final_list_type = "WAITLIST_HOLDING"
                seq_res = supabase.table("event_signups").select("id", count="exact").eq("event_id", body.event_id).eq("list_type", "WAITLIST_HOLDING").execute()
                sequence = (seq_res.count or 0) + 1

        # 3. Execute Insert
        payload = {
            "event_id": body.event_id,
            "user_id": profile["id"],
            "list_type": final_list_type,
            "sequence_number": sequence,
            "tier": eligibility.get("tier"), # Store tier for sorting later
            "is_guest": body.is_guest,
            "guest_name": body.guest_name
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
        if body.signup_id:
            current_signup_res = supabase.table("event_signups")\
                .select("*")\
                .eq("id", body.signup_id)\
                .eq("user_id", target_profile_id)\
                .maybe_single()\
                .execute()
        else:
            current_signup_res = supabase.table("event_signups")\
                .select("*")\
                .eq("event_id", body.event_id)\
                .eq("user_id", target_profile_id)\
                .eq("is_guest", False)\
                .maybe_single()\
                .execute()
            
        if not current_signup_res.data:
            return {"status": "success", "message": "Signup not found (already removed?)"}

        current_data = current_signup_res.data

        # 2. Determine signups to remove
        signups_to_remove_ids = [current_data["id"]]
        if not current_data.get("is_guest"):
            guests_res = supabase.table("event_signups").select("id").eq("event_id", body.event_id).eq("user_id", target_profile_id).eq("is_guest", True).execute()
            if guests_res.data:
                signups_to_remove_ids.extend([g["id"] for g in guests_res.data])

        # 3. Process each removal carefully to preserve list continuous sequences
        for s_id in signups_to_remove_ids:
            fresh_res = supabase.table("event_signups").select("*").eq("id", s_id).maybe_single().execute()
            if not fresh_res.data:
                continue

            fresh_data = fresh_res.data
            current_list_type = fresh_data["list_type"]
            current_seq = fresh_data["sequence_number"]
            
            # Delete the signup
            supabase.table("event_signups").delete().eq("id", fresh_data["id"]).execute()
            
            # Decrement sequences for the same list
            to_update_res = supabase.table("event_signups")\
                .select("id, sequence_number")\
                .eq("event_id", body.event_id)\
                .eq("list_type", current_list_type)\
                .gt("sequence_number", current_seq)\
                .execute()
                
            for row in to_update_res.data:
                new_seq = row['sequence_number'] - 1
                supabase.table("event_signups").update({"sequence_number": new_seq}).eq("id", row['id']).execute()
                
            # 4. Auto-Promote if needed (Steady State)
            if current_list_type == "EVENT":
                event = fetch_event(body.event_id)
                current_roster_count = fetch_counts(body.event_id)
                
                if current_roster_count < event['max_signups']:
                    print(f"Space opened in Roster ({current_roster_count} < {event['max_signups']}). Checking Waitlist...")
                    
                    next_up_res = supabase.table("event_signups")\
                        .select("*")\
                        .eq("event_id", body.event_id)\
                        .eq("list_type", "WAITLIST")\
                        .order("sequence_number", desc=False)\
                        .limit(1)\
                        .execute()
                        
                    if next_up_res.data:
                        next_person = next_up_res.data[0]
                        print(f"Promoting user {next_person['user_id']} from WAITLIST to EVENT")
                        
                        new_roster_seq = current_roster_count + 1
                        
                        supabase.table("event_signups").update({
                            "list_type": "EVENT",
                            "sequence_number": new_roster_seq
                        }).eq("id", next_person["id"]).execute()
                        
                        if event.get("status") == "FINAL_ORDERING":
                            try:
                                dropout_profile = supabase.table("profiles").select("full_name").eq("id", fresh_data["user_id"]).single().execute()
                                dropout_name = dropout_profile.data.get("full_name") if dropout_profile.data else "A player"
                                
                                promoted_profile = supabase.table("profiles").select("full_name").eq("id", next_person["user_id"]).single().execute()
                                promoted_name = promoted_profile.data.get("full_name") if promoted_profile.data else "A waitlist player"
                                
                                res_emails = supabase.table("event_signups").select("profiles!inner(email)").eq("event_id", body.event_id).in_("list_type", ["EVENT", "WAITLIST"]).execute()
                                all_emails = [row["profiles"]["email"] for row in res_emails.data if row.get("profiles") and row["profiles"].get("email")]
                                
                                email_service.send_late_stage_change_notification(event, dropout_name, promoted_name, all_emails)
                            except Exception as email_err:
                                print(f"Error sending late-stage promotion email: {email_err}")

                        wl_update_res = supabase.table("event_signups")\
                            .select("id, sequence_number")\
                            .eq("event_id", body.event_id)\
                            .eq("list_type", "WAITLIST")\
                            .gt("sequence_number", 1)\
                            .execute()
                            
                        for row in wl_update_res.data:
                            new_seq = row['sequence_number'] - 1
                            supabase.table("event_signups").update({"sequence_number": new_seq}).eq("id", row['id']).execute()

        return {"status": "success", "message": "Signup removed"}
    except Exception as e:
        print(f"Error removing signup: {e}")
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail="Failed to remove signup")


@app.get("/api/events")
async def get_events(request: Request, filter: str = "future"):
    # Authenticated endpoint to list events
    await get_current_user(request)
    
    now = get_now()
    query = supabase.table("events").select("*, event_types(*)")
    
    if filter == "future":
        query = query.gte("event_date", now.isoformat())
    elif filter == "past":
        query = query.lt("event_date", now.isoformat())
        
    # User requested chronological order
    events_res = query.order("event_date").execute()
        
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
    # Try admin auth first
    is_admin = False
    auth_header = request.headers.get("Authorization")
    if auth_header:
        try:
            await check_admin(request)
            is_admin = True
        except:
            pass

    expected_secret = os.environ.get("CRON_SECRET")
    cron_header = request.headers.get("X-Cron-Secret")
    force_generation = request.query_params.get("force_generation") == "true"
    
    if not is_admin:
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
        
        # Helper to fetch group email
        def get_group_email(group_id):
            if not group_id: return None
            res = supabase.table("user_groups").select("group_email").eq("id", group_id).single().execute()
            return res.data.get("group_email") if res.data else None

        # Helper to fetch user emails by signup list type
        def get_signup_emails(event_id, list_types):
            res = supabase.table("event_signups").select("profiles!inner(email)").eq("event_id", event_id).in_("list_type", list_types).execute()
            if not res.data: return []
            return [row["profiles"]["email"] for row in res.data if row.get("profiles") and row["profiles"].get("email")]

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
                        "event_id": str(event["id"]),
                        "user_id": str(update["user_id"]),
                        "list_type": update["list_type"],
                        "sequence_number": update["sequence_number"]
                    })
                
                print(f"Executing RPC for Preliminary Randomization ({len(update_list)} updates)...")
                
                try:
                    # Direct Update: Upsert list changes then update status
                    if update_list:
                        print(f"Executing Batch Upsert for {len(update_list)} records...")
                        supabase.table("event_signups").upsert(update_list).execute()
                    
                    print(f"Updating Event Status to {target_status}...")
                    supabase.table("events").update({"status": target_status}).eq("id", event["id"]).execute()
                    
                    try:
                        # Email Trigger Phase 4: Initial Schedule Notification
                        roster_group_email = get_group_email(event.get("roster_user_group"))
                        # Anyone in EVENT, WAITLIST, or WAITLIST_HOLDING gets the email
                        reserve_emails = get_signup_emails(event["id"], ["EVENT", "WAITLIST", "WAITLIST_HOLDING"])
                        email_service.send_initial_schedule_notification(event, roster_group_email, reserve_emails)
                    except Exception as e:
                        print(f"Email error (Initial Schedule): {e}")

                    processed_count += 1
                    
                except Exception as db_e:
                    print(f"CRITICAL: DB Update Failed for Event {event['id']}: {db_e}")
                    continue
            else:
                 # No one in holding? Just update status.
                 try:
                    supabase.table("events").update({"status": target_status}).eq("id", event["id"]).execute()
                    
                    try:
                        roster_group_email = get_group_email(event.get("roster_user_group"))
                        reserve_emails = get_signup_emails(event["id"], ["EVENT", "WAITLIST", "WAITLIST_HOLDING"])
                        email_service.send_initial_schedule_notification(event, roster_group_email, reserve_emails)
                    except Exception as e:
                        print(f"Email error (Initial Schedule): {e}")
                        
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
                        "event_id": str(event["id"]),
                        "user_id": str(update["user_id"]),
                        "list_type": update["list_type"],
                        "sequence_number": update["sequence_number"]
                    })
                
                print(f"Executing RPC for Final Promotion ({len(update_list)} updates)...")
                
                try:
                    # Direct Update: Upsert list changes then update status
                    if update_list:
                        print(f"Executing Batch Upsert for {len(update_list)} records...")
                        supabase.table("event_signups").upsert(update_list).execute()
                        
                    print(f"Updating Event Status to {target_status}...")
                    supabase.table("events").update({"status": target_status}).eq("id", event["id"]).execute()
                    
                    try:
                        # Email Trigger Phase 4: Final Schedule Notification
                        roster_group_email = get_group_email(event.get("roster_user_group"))
                        lineup_emails = get_signup_emails(event["id"], ["EVENT", "WAITLIST"])
                        email_service.send_final_schedule_notification(event, roster_group_email, lineup_emails)
                    except Exception as e:
                        print(f"Email error (Final Schedule): {e}")

                    processed_count += 1
                    promoted_count += len(update_list)
                    
                except Exception as db_e:
                     print(f"CRITICAL: DB Update Failed for Event {event['id']}: {db_e}")
                     continue
            else:
                 # No one in holding? Just update status.
                 try:
                    supabase.table("events").update({"status": target_status}).eq("id", event["id"]).execute()
                    
                    try:
                        roster_group_email = get_group_email(event.get("roster_user_group"))
                        lineup_emails = get_signup_emails(event["id"], ["EVENT", "WAITLIST"])
                        email_service.send_final_schedule_notification(event, roster_group_email, lineup_emails)
                    except Exception as e:
                        print(f"Email error (Final Schedule): {e}")

                    processed_count += 1
                 except Exception as e:
                    print(f"Error updating status to FINAL for {event['id']}: {e}")

        else:
            # 3. Simple Transition (e.g. NOT_YET_OPEN -> OPEN_FOR_ROSTER)
            # Use RPC ensuring it is transactional even if just one update
            print(f"Executing Direct Update (Status Only update)...")
            try:
                supabase.table("events").update({"status": target_status}).eq("id", event["id"]).execute()
                
                try:
                    # Email Trigger Phase 4: Signup Opens
                    if target_status == "OPEN_FOR_ROSTER" and current_status != "OPEN_FOR_ROSTER":
                        roster_group_email = get_group_email(event.get("roster_user_group"))
                        email_service.send_roster_open_notification(event, roster_group_email)
                    elif target_status == "OPEN_FOR_RESERVES" and current_status != "OPEN_FOR_RESERVES":
                        # Both T1 and T2 reserves get the email (send twice or combine)
                        t1_email = get_group_email(event.get("reserve_first_priority_user_group"))
                        t2_email = get_group_email(event.get("reserve_second_priority_user_group"))
                        if t1_email: email_service.send_reserve_open_notification(event, t1_email)
                        if t2_email and t2_email != t1_email: email_service.send_reserve_open_notification(event, t2_email)
                except Exception as e:
                    print(f"Email error (Window Open): {e}")

                processed_count += 1
            except Exception as e:
                print(f"Error updating status for {event['id']}: {e}")

    # --- FUTURE EVENT GENERATION ROUTINE ---
    # To prevent spamming DB inserts every 5 minutes, we only run generation 
    # roughly once a day. If it runs every 5 minutes, checking during the 00-05 minute mark
    # of a specific hour will make it run exactly once per day.
    # We choose 8:00 AM UTC (Midnight PT during PST, 1 AM during PDT).
    # We choose 8:00 AM UTC (Midnight PT during PST, 1 AM during PDT).
    generated_count = 0
    if force_generation or (now.hour == 8 and now.minute < 5):
        reason = "Manual force" if force_generation else "Daily trigger"
        print(f"{reason} reached. Generating future events...")
        try:
            generated_count = generate_future_events(supabase, days_ahead_to_ensure=14)
            print(f"Generated {generated_count} new events.")
        except Exception as e:
            print(f"Error during scheduled event generation: {e}")

    return {
        "status": "completed", 
        "processed_events": processed_count, 
        "users_promoted": promoted_count,
        "events_generated": generated_count
    }



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
