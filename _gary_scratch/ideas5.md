# ideas5.md - Consolidated Remaining Work

This document tracks all remaining tasks for the Sport Event Scheduling App. Fully implemented items, including the **Google Workspace Configuration** and **Domain Migration to bethamhoops.skeddle.net**, have been removed.

## 1. Data Integrity & Auth Audit

*   **Authentication & Data Audit:** 
    *   Audit Supabase tables for inconsistencies between audit, users, and profile records.
    *   Audit for duplicate names or emails.
    *   **Auth Method Indication:** Show on the user's profile and the Admin's users page whether they are using Google Authentication or a password.
    *   **User Education/Switching:** Add a simple help tip or guidance on the user profile page explaining how to switch or link their authentication methods.
    *   **Status:** Completed (Audit script verified, Profile page implemented with auth switching guidance).

## 2. User Import

*   **User CSV Import:** Prepare and execute a bulk import of users into the system.
    *   **Status:** Not Yet Implemented
    *   **Manual Steps (User):** Provide the current source CSV file for mapping.

## 3. Ongoing Bug Fixes

 *   Admin Trigger Scheduler gives error "Error: Unauthorized"/ Fix this.

*   **General Bug Fixes:** 
    *   Fix "Cancelled Date" timezone issue (where dates might shift due to UTC conversion).
    *   Fix "Guest Placement Bug" (ensuring guests are correctly prioritized/placed in the waitlist).
    *   **Status:** Partially Implemented (Awaiting specific identification during manual testing).

## 4. Email System & Communication

*   **Email System Audit:**
    *   Document all system-generated emails, including triggers (when), recipients (who), and content.
    *   Update user documentation to clearly explain the automated email workflow.
*   **Support Channel:**
    *   Add a feature for users to report problems or send direct inquiries to the administrator.

## 5. UI/UX & Terminology Refinement

*   **Terminology Audit:**
    *   Identify and replace instances of "roster" within the signup sequence with more appropriate terms (e.g., "signup list"). Note that  "roster" is correctly used to refer to user groups sometimes -- do not change those references.

*   **Auth Method Accuracy:**
    *   On user admin page, the authentication method of every user says email even though I know some users use Google authentication.  Fix this.

---

### Manual Steps Summary for You (The User):

1.  **CSV Source Data:** Provide the source CSV file for preparing the user import.
