# ideas5.md - Consolidated Remaining Work

This document tracks all remaining tasks for the Sport Event Scheduling App, consolidating items from `ideas4a.md` and `ideas4b.md`. Fully implemented items have been removed.

## 1. Google Workspace & Group Management

*   **Google Workspace API Credentials:** Verified. I checked the existing `backend/google-credentials.json` and successfully tested connectivity to the Google Admin SDK.
    *   **Status:** Completed
    *   **Manual Steps (User):** None remaining. Credentials and domain-wide delegation are fully functional.
*   **Create Reserves Groups:** Configured and synced 6 new groups in the database for both Roster and Reserves. `google_group_id` was removed from the codebase.
    *   **Status:** Completed
    *   **Manual Steps (User):** Optionally drop the `google_group_id` column physically from the database using `database/migrations/20260310_sync_google_groups.sql` in the Supabase Dashboard.

## 2. Infrastructure & Hosting

*   **Hosting Migration:** Change hosting to `bethamhoops.skeddle.net`.
    *   **Status:** Not Yet Implemented
    *   **Manual Steps (User):** Perform the domain switch and update hosting environment variables as needed.

## 3. Data Integrity & Auth Audit

*   **Authentication & Data Audit:** 
    *   Audit Supabase tables for inconsistencies between audit, users, and profile records.
    *   Audit for duplicate names or emails.
    *   **Auth Method Indication:** Show on the user's profile and the Admin's users page whether they are using Google Authentication or a password.
    *   **User Education/Switching:** Add a simple help tip or guidance on the user profile page explaining how to switch or link their authentication methods.
    *   **Status:** Pending (Currently blocked by the lack of a non-admin profile page and the complexity of accessing `auth.users` data).

## 4. User Import

*   **User CSV Import:** Prepare and execute a bulk import of users into the system.
    *   **Status:** Not Yet Implemented
    *   **Manual Steps (User):** Provide the current source CSV file for mapping.

## 5. Ongoing Bug Fixes

*   **General Bug Fixes:** 
    *   Fix "Cancelled Date" timezone issue (where dates might shift due to UTC conversion).
    *   Fix "Guest Placement Bug" (ensuring guests are correctly prioritized/placed in the waitlist).
    *   **Status:** Partially Implemented (Awaiting specific identification during manual testing).

---

### Manual Steps Summary for You (The User):

1.  **Generate API Credentials:** Create a service account or OAuth credentials in Google Cloud Console.
2.  **Create Google Groups:** Manually create "Sunday Reserves", "Tuesday Reserves", and "Thursday Reserves" groups in your Workspace console.
3.  **Hosting Migration:** Switch domain to `bethamhoops.skeddle.net`.
4.  **CSV Source Data:** Provide the source CSV file for preparing the user import.
