# Scheduler Technical Documentation

This document explains how the event scheduling and status lifecycle works in the application.

## 1. Status Lifecycle
Events follow a strict linear progression of statuses. The transition is driven by the `trigger_schedule` cron job.

| Status | Meaning |
| :--- | :--- |
| `NOT_YET_OPEN` | Event is created but signups are not yet active for anyone. |
| `OPEN_FOR_ROSTER` | Signups are open only for Tier 1 (Roster) members. |
| `OPEN_FOR_RESERVES` | Signups are open for Tier 2 and Tier 3 (Reserves). Reserves enter the **Holding Queue**. |
| `PRELIMINARY_ORDERING` | The transition point where the Holding Queue is randomized by Tier. |
| `FINAL_ORDERING` | Users are promoted from Holding into the Event or Waitlist based on available spots. |
| `FINISHED` | The event has passed (Start Time + Duration). |
| `CANCELLED` | Manual override or auto-cancelled via Blackout Dates. |

## 2. Event Generation
Events are automatically generated **14 days in advance** by the `generate_future_events` function.

- **Frequence:** Runs once daily (triggered by the cron job at 8:00 AM UTC).
- **Blackout Dates:** The system checks the `cancelled_dates` table. If an event falls on a blacklisted date, it is created with a `CANCELLED` status immediately to prevent signups.

## 3. The Sync (Cron) Job
The `POST /api/trigger_schedule` endpoint performs the following tasks:
1. **Status Update:** Recalculates the status for all active events based on the current UTC time.
2. **Holding Promotions:** When an event enters `PRELIMINARY_ORDERING`, it randomizes the group of Reserves and promotes them.
3. **Daily Generation:** Once a day, it triggers the creation of new events for the 2-week rolling window.

## 4. Randomization Logic
Promotion from the Holding Area is prioritized by Tier:
1. **Tier 2 (First Priority Reserves):** All Tier 2 users are randomized among themselves.
2. **Tier 3 (Second Priority Reserves):** All Tier 3 users are randomized among themselves and placed after Tier 2.

Users are then moved into the `EVENT` list until `max_signups` is reached, after which they are moved into the `WAITLIST`.
