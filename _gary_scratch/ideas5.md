# ideas5.md - Consolidated Remaining Work

This document tracks all remaining tasks for the Sport Event Scheduling App. Fully implemented items, including the **Google Workspace Configuration** and **Domain Migration to bethamhoops.skeddle.net**, have been removed.

## 1. Data Integrity & Auth Audit

*   **Authentication & Data Audit:** 
    *   Audit Supabase tables for inconsistencies between audit, users, and profile records.
    *   Audit for duplicate names or emails.
    *   **Auth Method Indication:** Show on the user's profile and the Admin's users page whether they are using Google Authentication or a password.
    *   **User Education/Switching:** Add a simple help tip or guidance on the user profile page explaining how to switch or link their authentication methods.
    *   **Status:** Pending (Currently blocked by the lack of a non-admin profile page and the complexity of accessing `auth.users` data).

## 2. User Import

*   **User CSV Import:** Prepare and execute a bulk import of users into the system.
    *   **Status:** Not Yet Implemented
    *   **Manual Steps (User):** Provide the current source CSV file for mapping.

## 3. Ongoing Bug Fixes

*   **General Bug Fixes:** 
    *   Fix "Cancelled Date" timezone issue (where dates might shift due to UTC conversion).
    *   Fix "Guest Placement Bug" (ensuring guests are correctly prioritized/placed in the waitlist).
    *   **Status:** Partially Implemented (Awaiting specific identification during manual testing).

---

### Manual Steps Summary for You (The User):

1.  **CSV Source Data:** Provide the source CSV file for preparing the user import.
