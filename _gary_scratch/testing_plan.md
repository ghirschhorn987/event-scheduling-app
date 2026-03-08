# End-to-End Testing Plan

This document outlines the step-by-step test flows required to confidently deploy and operate Skeddle. Each area targets the core logic of the scheduling algorithm and notification service.

## 1. Supabase Auth & Profile Initialization
- **Action:** Sign up a new user via Google.
- **Expected:** An Auth user is created. The first time they log in or hit an endpoint, a row in the `profiles` table is securely initialized.
- **Validation:** View the Admin Approvals dashboard to see the new request.

## 2. Admin Approvals & Group Assignment
- **Action:** Approve the test user from step 1. Assign them to a specific group (e.g., `Tuesday Roster`).
- **Expected:** The user's row in `event_users` or joining table is updated. The user can now see their group in `Admin Users`.
- **Validation:** Check the `user_groups` table to ensure membership is recorded accurately.

## 3. Event Generation (Cron Simulator)
- **Action:** Click "Trigger Scheduler" in Admin Hub.
- **Expected:** New events are generated exactly two weeks ahead, matching the `event_types` schedules.
- **Validation:** Verify `events` table. Dates marked in `cancelled_dates` should be explicitly inserted with `status = CANCELLED`.

## 4. Phase 1: Roster Signups (Tier 1)
- **Action:** Manually set an event status to `OPEN_FOR_ROSTER`. Impersonate a Tier 1 user and click "Join".
- **Expected:** User is added directly to `list_type: EVENT` with an incrementing `sequence_number`.

## 5. Phase 2: Reserve Holding Queue (Tier 2/3)
- **Action:** Set event status to `OPEN_FOR_RESERVES`. Have 3 Tier 2 users and 2 Tier 3 users join.
- **Expected:** All 5 users are placed in `list_type: WAITLIST_HOLDING`.
- **Validation:** They are not assigned to `EVENT` yet, regardless of capacity.

## 6. Phase 3: Waitlist Assignments
- **Action:** The event enters `PRELIMINARY_ORDERING` (trigger cron). 
- **Expected:** The 5 users are moved out of Holding. Tier 2 is randomly shuffled first, then Tier 3. They are placed into `EVENT` if room exists, otherwise `WAITLIST`.
- **Validation:** Database records reflect standard Event/Waitlist distribution. Expected emails ("Preliminary Schedule Released") should fire.

## 7. Phase 4: Open Access (Waitlist Queue)
- **Action:** Set event status to `FINAL_ORDERING`. Have a new user try to join.
- **Expected:** Because `PRELIMINARY_ORDERING` has already passed, the user is immediately appended to the end of the `WAITLIST`.

## 8. Auto-Promotions
- **Action:** Have a user in `EVENT` click "Remove".
- **Expected:** The user is removed. The person at `WAITLIST` sequence 1 is promoted to `EVENT`. The rest of the waitlist has their sequences decremented.
- **Validation:** "Late Stage Change" emails are triggered locally via `email_service.py` logs.

## 9. Admin Overrides
- **Action:** Admin clicks "Make Roster Full" or manually deletes a signup from the `Admin Event Detail` page.
- **Expected:** Actions behave identical to user-initiated actions, gracefully handling sequences and list promotions. 
