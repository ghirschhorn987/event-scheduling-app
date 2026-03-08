# ideas4.md - Consolidated Remaining Work

This document tracks all remaining tasks for the Sport Event Scheduling App, consolidating items from `ideas.md`, `ideas2.md`, and `scratch2.md`. Fully implemented items have been removed.

### Phase 1: Infrastructure & Data Model Updates

*   **Google Workspace Upgrade:** Purchase the lowest-tier "Business Plan" for Google Workspace to enable API access for Google Groups integration.
    *   **Status:** Not Yet Implemented
    *   **Manual Steps (User):** Go to Google Workspace, purchase/upgrade the account to the basic Business Plan, and generate the necessary API credentials.
*   **Hosting Migration:** Change hosting to `bethamhoops.skeddle.net`.
    *   **Status:** Not Yet Implemented
    *   **Manual Steps (User):** Perform the domain switch and update hosting environment variables as needed.

### Phase 2: User & Group Management

*   **New Group Creation:** Create three new User Groups (and corresponding Google Groups) for reserves: Sunday Reserves, Tuesday Reserves, Thursday Reserves.
    *   **Status:** Not Yet Implemented (Both)
    *   **Manual Steps (User):** Manually create the corresponding Google Groups in your Google Workspace admin console. *(The Supabase side can be done manually by you via the Admin UI, or automated by me).*
*   **Sync Logic Implementation:** Develop a function to read users from a Supabase User Group ("ground truth") and sync them to the associated Google Group. Create a mechanism to identify discrepancies, and optionally a reverse-sync.
    *   **Status:** Partially Implemented (Automated effort by AI)
    *   *Note:* The backend currently has a mock service for this (`mock_google_service.py`). It needs to be replaced with real Google API calls once the Workspace is upgraded.
*   **User Group Type Clarification:** Explain or rename type values on the User Groups page to be clearer.
    *   **Status:** Not Yet Implemented (Automated effort by AI)

### Phase 3: Event Lifecycle & Scheduling Logic

*   **Automated Event Generation & Blackout Dates:** Create a generator that ensures events are created two weeks in advance, respecting the "Canceled Dates" from the admin.
    *   **Status:** Partially Implemented (Automated effort by AI)
*   **Automated Status Updates (Finished Status):** Ensure events are not marked as "Closed/Finished" until after the Event Start Time PLUS the Event Duration.
    *   **Status:** Partially Implemented (Automated effort by AI)
*   **Final Ordering Flexibility:** Ensure users can still add or remove sign-ups when an event is in "Final Ordering" status.
    *   **Status:** Partially Implemented (Automated effort by AI)
*   **Manual Scheduler Trigger:** Add a button to the admin interface to immediately invoke the scheduler logic.
    *   **Status:** Not Yet Implemented (Automated effort by AI)

### Phase 4: Notification System (Email Triggers)

*   **Notification System Integration:** Fully integrate signup open, initial schedule, final schedule, and late-stage change emails into the scheduler logic.
    *   **Status:** Partially Implemented (Automated effort by AI)
*   **Email Content Review:** Review and finalize the text/templates for all automated emails.
    *   **Status:** Partially Implemented (Automated effort by AI)

### Phase 5: Admin Tools & Audit

*   **Enhanced Edit Event Type UI:** Display and accept time in hours and minutes instead of just minutes. Remove "(minutes)" or "(min)" labels.
    *   **Status:** Partially Implemented (Automated effort by AI)
*   **Registration Requests (Approve Accounts) Filtering:** Add status filters (hide approved/rejected by default) and rename to "Registration Requests".
    *   **Status:** Not Yet Implemented (Automated effort by AI)
*   **Authentication & Data Audit:** 
    *   Audit Supabase tables for inconsistencies between audit, users, and profile records.
    *   Audit for duplicate names or emails.
    *   Show on users page whether someone is using Google Auth or a password. 
    *   **Status:** Not Yet Implemented (Automated effort by AI)
*   **User CSV Import Preparation:** Prepare a CSV file for bulk import into the system based on your existing data.
    *   **Status:** Not Yet Implemented (Both)
    *   **Manual Steps (User):** Provide the current source CSV file for mapping.

### Phase 6: UI/UX Enhancements

*   **Event List Management:** List events in chronological order, add past/future and status filters, and default to future events. Rename "Upcoming Events" to "Events".
    *   **Status:** Partially Implemented (Automated effort by AI)
*   **Redesigned Header/Event Sign-up Lists:** Remove "Toggle Email View"; always display email in the header and in event lists.
    *   **Status:** Partially Implemented (Automated effort by AI)
*   **Upcoming Events UI:** Make the Day (3-day abbr) and Date (3-day Month + Day) more prominent than the time.
    *   **Status:** Not Yet Implemented (Automated effort by AI)
*   **Onboarding/Signup Refactor:** 
    *   Move the "New To The Game" workflow to a dedicated page with clearer explanations.
    *   Add a disclaimer on the Google Login screen about the "supabase.com" redirect being normal and safe.
    *   **Status:** Not Yet Implemented (Automated effort by AI)

### Phase 7: Testing, Help & Fixes

*   **Manual Testing Plan:** Create a comprehensive, step-by-step test plan for manually verifying all scheduling features, ordered by priority.
    *   **Status:** Not Yet Implemented (Automated effort by AI)
*   **User & Admin Help Pages:** Add a non-admin help page (userPerspective) and a technical admin help page.
    *   **Status:** Not Yet Implemented (Automated effort by AI)
*   **Bug Fixes:** 
    *   Fix the "Cancelled Date" timezone issue where it applies to the day before.
    *   Fix the "Guest Placement Bug" where guests may be skipping the holding list.
    *   **Status:** Partially Implemented (Automated effort by AI)

---

### Manual Steps Summary for You (The User):
1.  **Purchase Google Workspace Business Plan:** Upgrade your account to permit Google Groups API access.
2.  **Generate API Credentials:** Create a service account or OAuth credentials in Google Cloud Console.
3.  **Create Google Groups:** Manually create "Sunday Reserves", "Tuesday Reserves", and "Thursday Reserves" groups in your Workspace console.
4.  **Hosting Migration:** Switch domain to `bethamhoops.skeddle.net`.
5.  **CSV Source Data:** Provide the source CSV file for preparing the user import.
6.  **Auth Method Education:** Help users understand how to check if they sign in via Google or password (if not already obvious).
