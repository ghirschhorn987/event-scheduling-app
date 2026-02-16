# Project Implementation Status Report

Based on a review of `_gary_scratch` documents (`ideas.md`, `ideas2.md`, `scratch.md`, `scratch2.md`) and the current codebase.

## 1. Not Implemented At All

*   **Automated Event Generation**: The scheduler (`/api/schedule`) only updates statuses of existing events. It does not generate new events 2 weeks in advance as requested.
*   **Google Groups Integration**:
    *   No backend logic for syncing Supabase User Groups to Google Groups.
    *   No "Sync" button on the Admin Configuration page.
*   **Notification System**:
    *   No emails are triggered by the scheduler (for "Open for Roster", "Open for Reserves", "Preliminary Ordering", "Final Ordering", or "Late-Stage Changes").
    *   `email_service.py` exists but is only used for registration requests/approvals, not event lifecycle.
*   **Event Management Screen**:
    *   There is no Admin UI to list all events, cancel them, or override their statuses.
    *   No "Blackout Dates" configuration interface.
*   **Out-of-Town Guest Feature**:
    *   No UI for adding guests.
    *   No backend logic for "dummy profiles" or guest placeholders.
    *   No `Guest Permissions` column found in `user_groups` table.
*   **User Group Types**:
    *   The `User Group Type` column (Event Eligibility, Application Role, etc.) is missing from the `user_groups` table schema.
*   **Specific Reserve Groups**:
    *   The database migration `refactor_user_management.sql` seeds "Primary" and "Secondary" groups, but does not create the specific "Sunday Reserves", "Tuesday Reserves", or "Thursday Reserves" groups mentioned in the plan.

## 2. Partially Implemented

*   **Scheduler / State Transitions**:
    *   **Implemented**: The structure for time-based status transitions exists.
    *   **Implemented**: `PRELIMINARY_ORDERING` correctly randomizes the holding queue (by tiers) and assigns sequence numbers.
    *   **Implemented**: `FINAL_ORDERING` correctly promotes users based on the established sequence order without re-randomizing.
    *   **Missing**: The scheduler does NOT handle `CANCELLED` events (except to skip them), and there is no logic to "un-cancel" or manually override statuses via the API.
*   **Event Duration**:
    *   **Implemented**: `Duration` column was added to the `events` table via SQL migration.
    *   **Missing**: `ideas2.md` requested moving `Duration` to the `event_types` table. Use of duration in frontend/backend logic is inconsistent or missing (Admin UI for Event Types does not show a Duration field).
*   **Dropout Logic**:
    *   **Implemented**: `api/remove-signup` correctly promotes the next person from `WAITLIST` to `EVENT`.
    *   **Missing**: It does not send a notification to the promoted user.

## 3. Fully Implemented (But Different Manner)

*   **Event Duration Location**:
    *   *Requirement*: Move `Duration` to `Event Type` table.
    *   *Implementation*: Added `duration` column to `Events` table (`add_status_determinant_and_duration.sql`).
*   **User Group Naming**:
    *   *Requirement*: `ideas.md` suggests specific groups like "TuesdayBasketballReserves".
    *   *Implementation*: The system seems to rely on generic "Primary" / "Secondary" groups seeded in the DB, though the schema supports any group names.

## 4. Implemented as Suggested

*   **Event Status Enum**: The `EventStatus` enum in `models.py` matches the scratch file definitions (`NOT_YET_OPEN` ... `FINISHED`, `CANCELLED`).
*   **Signup Eligibility Logic**: `check_signup_eligibility` in `logic.py` correctly implements the rules.
*   **Randomization Logic**: `randomize_holding_queue` in `logic.py` correctly implements the tiered randomization.
