# Implementation Prompt for Event Scheduling App Refinements

Please implement the following updates and refinements to the Event Scheduling application.

## 1. Sync Admin Events Page with Events Page - COMPLETED
**Target Files:** `frontend/src/pages/AdminEvents.jsx`, `backend/main.py` (specifically `list_admin_events`)

*   **Filters & Sort Order:** Update the **Admin Events** page to include the same `timeFilter` ("Future", "Past", "All") and `statusFilter` ("All", "Open for Roster", etc.) found on the main **Events** page (`EventsListPage.jsx`).
*   **Default Settings:** Set the default view to show "Future Events" sorted by date (ascending, so the soonest event is first), matching the user-facing page.
*   **Backend Support:** Ensure the `/api/admin/events` endpoint supports these filters or reuse the logic from the `/api/events` endpoint to ensure consistency in data retrieval.

## 2. Terminology Consistency - COMPLETED
**Target Files:** `frontend/src/pages/AdminEventDetail.jsx`, `frontend/src/pages/Dashboard.jsx` (and any related components/modals)

Ensure consistent terminology for signup lists while preserving technical/group names:
*   **Rename Signup Lists:** Everywhere a user list is shown for an event, use the labels **"Signed Up"**, **"Waitlist"**, and **"Holding Area"**.
    *   In `AdminEventDetail.jsx`: Rename "Roster" section to "Signed Up" and "Holding Queue" to "Holding Area".
    *   In `Dashboard.jsx`: Rename the "Roster" count/label in the summary and the section headers.
*   **Preserve Technical Terms:** 
    *   Continue using **"Roster"** to refer to the priority user groups (e.g., in the Group Management screens).
    *   Do **NOT** change the event status enum `OPEN_FOR_ROSTER` or its display text where it refers specifically to the status (e.g., status badges).

## 3. Remove Guest Functionality - COMPLETED
**Target Files:** `frontend/src/pages/Dashboard.jsx`, `backend/main.py`

*   **Guest Management:** Enable users to easily remove their own guests from an event.
*   **Fix Dashboard Logic:** In `Dashboard.jsx`, ensure the "Remove" button appears correctly for guests when the sponsor is viewing the page. Note: Verify that `s.user_id` is compared against the Profile ID (`userProfile.id`) and not the Auth ID (`session.user.id`).
*   **UI Placement:** Add a "Remove" button next to each guest name in the "Out-of-Town Guests" management section of the Dashboard, in addition to the button in the main lists.

## 4. Event Status Information - COMPLETED
**Target File:** `frontend/src/pages/EventsListPage.jsx`

*   **Status Legend:** On the main Events list page (non-Help page), add a small informational section or tooltips explaining what the different status values mean:
    *   **Not Yet Open:** Scheduling has not started.
    *   **Open for Roster:** Priority roster members can sign up.
    *   **Open for Reserves:** Reserves can join the Holding Area.
    *   **Preliminary Ordering:** Holding Area randomized; initial placements visible.
    *   **Final Ordering:** Placements are locked; First-come, first-served for remaining spots.
    *   **Finished/Cancelled:** Self-explanatory.

## 5. Show Signup Counts in Admin Event Management - COMPLETED
**Target Files:** `frontend/src/pages/AdminEvents.jsx`, `backend/main.py`

*   **Display Counts:** In the event table on the **Manage Event Lists** (Admin Events) page, add a column for signup counts.
*   **Format:** Use the format `X / Y` (e.g., `12 / 5`), where `X` is the number of users in the "Signed Up" (Roster) list and `Y` is the combined count of users in the "Waitlist" and "Holding Area".
*   **Backend Update:** Update the `/api/admin/events` endpoint to include these counts in the response, similar to how they are provided in the `/api/events` endpoint.

***

### Technical Context for Implementation:
*   The **Frontend** is built with React/Vite using Tailwind CSS and HSL-based styling.
*   The **Backend** is FastAPI with Supabase as the database.
*   Use `userProfile.id` for matching signup ownership as `session.user.id` refers to the Supabase Auth internal UUID.
