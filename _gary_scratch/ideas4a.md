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
*   **Sync Logic Implementation:** Develop a function to read users from a Supabase User Group ("ground truth") and sync them to the associated Google Group. Since you don't have the Google Workspace capability yet, mock the function out so it logs what it *would* do and attach a "Sync Now" button to the User Groups admin page.
    *   **Status:** Completed
*   **User Group Type Clarification:** Explain or rename type values on the User Groups page to be clearer.
    *   **Status:** Completed

### Phase 3: Event Lifecycle & Scheduling Logic

*   **Automated Event Generation & Blackout Dates:** Create a generator that ensures events are created two weeks in advance, respecting the "Canceled Dates" from the admin.
    *   **Status:** Completed
*   **Automated Status Updates (Finished Status):** Ensure events are not marked as "Closed/Finished" until after the Event Start Time PLUS the Event Duration.
    *   **Status:** Completed
*   **Final Ordering Flexibility:** Ensure users can still add or remove sign-ups when an event is in "Final Ordering" status.
    *   **Status:** Completed
*   **Manual Scheduler Trigger:** Add a button to the admin interface to immediately invoke the scheduler logic.
    *   **Status:** Completed

### Phase 4: Notification System (Email Triggers)

*   **Notification System Integration:** Fully integrate signup open, initial schedule, final schedule, and late-stage change emails into the scheduler logic.
    *   **Status:** Completed
*   **Email Content Review:** Review and finalize the text/templates for all automated emails.
    *   **Status:** Completed

### Phase 5: Admin Tools & Audit

*   **Enhanced Edit Event Type UI:** Display and accept time in hours and minutes instead of just minutes. Remove "(minutes)" or "(min)" labels.
    *   **Status:** Completed
*   **Registration Requests (Approve Accounts) Filtering:** Add status filters (hide approved/rejected by default) and rename to "Registration Requests".
    *   **Status:** Completed
*   **Authentication & Data Audit:** 
    *   Audit Supabase tables for inconsistencies between audit, users, and profile records.
    *   Audit for duplicate names or emails.
    *   **Auth Method Indication:** Show on the user's profile and the Admin's users page whether they are using Google Authentication or a password.
    *   **User Education/Switching:** Add a simple help tip or guidance on the user profile page explaining how to switch or link their authentication methods (e.g., if they want to move from password to Google).
    *   **Status:** Blocked/Skipped (See blockers.md)
*   **User CSV Import Preparation:** Prepare a CSV file for bulk import into the system based on your existing data.
    *   **Status:** Not Yet Implemented (Both)
    *   **Manual Steps (User):** Provide the current source CSV file for mapping.

### Phase 6: UI/UX Enhancements

*   **Event List Management:** List events in chronological order, add past/future and status filters, and default to future events. Rename "Upcoming Events" to "Events".
    *   **Status:** Completed
*   **Redesigned Header/Event Sign-up Lists:** Remove "Toggle Email View"; always display email in the header and in event lists.
    *   **Status:** Completed
*   **Upcoming Events UI:** Make the Day (3-day abbr) and Date (3-day Month + Day) more prominent than the time.
    *   **Status:** Completed
*   **Onboarding/Signup Refactor:** 
    *   Move the "New To The Game" workflow to a dedicated page with clearer explanations.
    *   Add a disclaimer on the Google Login screen about the "supabase.com" redirect being normal and safe.
    *   **Status:** Completed

### Phase 7: Testing, Help & Fixes

*   **Manual Testing Plan:** Create a comprehensive, step-by-step test plan outline for yourself that covers all core flows (Signup, Waitlist logic, Auto-promotion, Email Triggers, Admin Overrides).
    *   **Status:** Completed (Wrote `_gary_scratch/testing_plan.md`)
*   **User & Admin Help Pages:** Add a non-admin help page explaining the scheduling rules and an admin help page linking to the architecture documents.
    *   **Status:** Completed
*   **Bug Fixes:** 
    *   Fix "Cancelled Date" timezone issue.
    *   Fix "Guest Placement Bug".
    *   **Status:** Partially Implemented (Will address when identified based on Testing Plan)

---

### Manual Steps Summary for You (The User):
1.  **Purchase Google Workspace Business Plan:** Upgrade your account to permit Google Groups API access.
2.  **Generate API Credentials:** Create a service account or OAuth credentials in Google Cloud Console.
3.  **Create Google Groups:** Manually create "Sunday Reserves", "Tuesday Reserves", and "Thursday Reserves" groups in your Workspace console.
4.  **Hosting Migration:** Switch domain to `bethamhoops.skeddle.net`.
5.  **CSV Source Data:** Provide the source CSV file for preparing the user import.
