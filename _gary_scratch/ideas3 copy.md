# ideas3.md - Consolidated Remaining Work

This document tracks items from `ideas1.md` (which was found as `ideas.md`) and `ideas2.md` that are **not fully implemented**. Fully implemented items (like the terminology refactor, database schema enhancements, guest features, and the base admin event screens) have been removed.

### Phase 1: Infrastructure & Data Model Updates

*   **Google Workspace Upgrade:** Purchase the lowest-tier "Business Plan" for Google Workspace to enable API access for Google Groups integration.
    *   **Status:** Not Yet Implemented
    *   **Manual Steps (User):** Go to Google Workspace, purchase/upgrade the account to the basic Business Plan, and generate the necessary API credentials.

### Phase 2: User & Group Management

*   **New Group Creation:** Create three new User Groups (and corresponding Google Groups) for reserves: Sunday Reserves, Tuesday Reserves, Thursday Reserves.
    *   **Status:** Not Yet Implemented (Both)
    *   **Manual Steps (User):** Manually create the corresponding Google Groups in your Google Workspace admin console. *(The Supabase side can be done manually by you via the Admin UI, or automated by me).*

*   **Sync Logic Implementation:** Develop a function to read users from a Supabase User Group ("ground truth") and sync them to the associated Google Group. Create a mechanism to identify discrepancies, and optionally a reverse-sync.
    *   **Status:** Partially Implemented (Automated effort by you [AI])
    *   *Note:* The backend currently has a mock service for this (`mock_google_service.py`). It needs to be replaced with real Google API calls once the Workspace is upgraded.

*   **Admin Interface:** Add a button to the User Groups admin page to manually trigger the sync function.
    *   **Status:** Partially Implemented (Automated effort by you [AI])
    *   *Note:* The backend endpoint exists, but we need to ensure the frontend button is fully wired up and functional with the real sync logic.

### Phase 3: Event Lifecycle & Scheduling Logic

*   **Automated Event Generation & Blackout Dates:** Create a generator that ensures events are created two weeks in advance, respecting a list of "Canceled Dates" from the admin.
    *   **Status:** Partially Implemented (Automated effort by you [AI])
    *   *Note:* The core generation logic and blackout tables exist, but we need to verify the scheduler cron job fully automates this continually.

*   **Automated Status Updates:** Implement logic to automatically mark an event as "Closed" once the time equals Start Time + Duration.
    *   **Status:** Partially Implemented (Automated effort by you [AI])
    *   *Note:* Basic status logic is in `logic.py`, but we need to verify the "Closed/Finished" transition runs perfectly on schedule.

*   **Documentation:** Produce a technical explanation of how the current scheduler works, specifically regarding status changes, execution frequency, and logic.
    *   **Status:** Not Yet Implemented (Automated effort by you [AI])
    *   *Note:* I can generate this documentation for you.

### Phase 4: Notification System (Email Triggers)

*   **Signup Open Notifications:** Email the specific Roster/Reserve Google Group when their signup window opens.
*   **Schedule Confirmation Notifications:** Email Initial Schedule and Final Schedule confirmations.
*   **Late-Stage Change Notifications:** Email everyone involved if a user drops out or a status changes late, highlighting who is promoted.
    *   **Status:** Partially Implemented (Automated effort by you [AI])
    *   *Note:* The email templates and sending functions exist in `email_service.py`, but they need to be fully integrated into the scheduler state transitions in `logic.py` and rigorously tested.

---

### Manual Steps Summary for You (The User):
1. **Purchase Google Workspace Business Plan:** Upgrade your account to permit Google Groups API access.
2. **Generate API Credentials:** Create a service account or OAuth credentials in Google Cloud Console for the Workspace integration.
3. **Create Google Groups:** Manually create the "Sunday Reserves", "Tuesday Reserves", and "Thursday Reserves" groups in your Google Workspace admin interface to prepare for the sync feature.
