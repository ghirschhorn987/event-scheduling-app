
import os
import sys

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from db import supabase

def verify_event_groups():
    print("=" * 60)
    print("VERIFYING EVENT TYPE GROUPS")
    print("=" * 60)
    
    # 1. Fetch Event Types with Group Names
    # We want to see: event_type.name -> roster_group.name, reserve1.name, reserve2.name
    
    # Supabase Join Syntax for multiple foreign keys to same table is tricky in one go if names collide?
    # Let's try select.
    
    print("Fetching event_types...")
    
    # We fetch raw and then fetch groups to map manually to be safe/clear
    types_res = supabase.table("event_types").select("*").execute()
    
    groups_res = supabase.table("user_groups").select("id, name").execute()
    group_map = {g['id']: g['name'] for g in groups_res.data}
    
    for et in types_res.data:
        print(f"\nEvent Type: {et['name']}")
        
        roster_id = et.get('roster_user_group')
        res1_id = et.get('reserve_first_priority_user_group')
        res2_id = et.get('reserve_second_priority_user_group')
        
        roster_name = group_map.get(roster_id, "NONE")
        res1_name = group_map.get(res1_id, "NONE")
        res2_name = group_map.get(res2_id, "NONE")
        
        print(f"  - Roster Group:       {roster_name}")
        print(f"  - First Priority:     {res1_name}")
        print(f"  - Second Priority:    {res2_name}")
        
        # Validation Logic
        expected_roster = et['name'].replace(" ", "") # "Sunday Basketball" -> "SundayBasketball"
        expected_res1 = "FirstPriority"
        expected_res2 = "SecondPriority"
        
        # Allow for "FirstPriority" vs "First Priority" if names vary, but strict check first
        fail = False
        if roster_name != expected_roster:
            print(f"    ❌ Roster Group mismatch! Expected {expected_roster}")
            fail = True
            
        if res1_name != expected_res1:
            print(f"    ❌ First Priority mismatch! Expected {expected_res1}")
            fail = True

        if res2_name != expected_res2:
            print(f"    ❌ Second Priority mismatch! Expected {expected_res2}")
            fail = True
            
        if not fail:
            print("    ✅ Configuration Correct")

if __name__ == "__main__":
    verify_event_groups()
