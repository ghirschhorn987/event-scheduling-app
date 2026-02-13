
```markdown
# Event Management Specification

## 1. Status Definitions & Constraints
*   **Active Statuses**: `NOT_YET_OPEN`, `OPEN_FOR_ROSTER`, `OPEN_FOR_RESERVES`, `PRELIMINARY_ORDERING`, `FINAL_ORDERING`, `FINISHED`, `CANCELLED`.
*   **Deprecated**: `SCHEDULED` must be removed from the codebase and database. Any existing references are bugs.

## 2. Signup Logic
Signups are processed into three lists: `EVENT`, `WAITLIST`, and `WAITLIST_HOLDING`.

| Event Status | Roster Member Action | Reserve Member Action |
| :--- | :--- | :--- |
| `CANCELLED`, `FINISHED`, `NOT_YET_OPEN` | Access Denied | Access Denied |
| `OPEN_FOR_ROSTER` | `EVENT` (until full) → `WAITLIST` | Access Denied |
| `OPEN_FOR_RESERVES` | `EVENT` (until full) → `WAITLIST` | `WAITLIST_HOLDING` |
| `PRELIMINARY_ORDERING` | `EVENT` (until full) → `WAITLIST` | `WAITLIST_HOLDING` |
| `FINAL_ORDERING` | `EVENT` (until full) → `WAITLIST` | `EVENT` (until full) → `WAITLIST` |

## 3. State Transition Logic (Cron)
A cronjob runs every 5 minutes. Each event transition must be executed within a **single database transaction**. If the status is `CANCELLED` or `FINISHED`, no processing occurs.

### Transition: `NOT_YET_OPEN` → `OPEN_FOR_ROSTER`
*   **Trigger**: `current_time >= open_for_roster_trigger`
*   **Action**: Update status to `OPEN_FOR_ROSTER`.

### Transition: `OPEN_FOR_ROSTER` → `OPEN_FOR_RESERVES`
*   **Trigger**: `current_time >= open_for_reserves_trigger`
*   **Action**: Update status to `OPEN_FOR_RESERVES`.

### Transition: `OPEN_FOR_RESERVES` → `PRELIMINARY_ORDERING`
*   **Trigger**: `current_time >= preliminary_ordering_trigger`
*   **Action**:
    1.  Group users in `WAITLIST_HOLDING` by Tier.
    2.  Randomize Tier 2 (First Priority) users.
    3.  Randomize Tier 3 (Second Priority) users.
    4.  Re-order `WAITLIST_HOLDING` such that all randomized Tier 2 users appear before randomized Tier 3 users.
    5.  Update status to `PRELIMINARY_ORDERING`.

### Transition: `PRELIMINARY_ORDERING` → `FINAL_ORDERING`
*   **Trigger**: `current_time >= final_ordering_trigger`
*   **Action**:
    1.  Move users from `WAITLIST_HOLDING` (in their established order) to the end of the `EVENT` list until the event capacity is reached.
    2.  Move any remaining users from `WAITLIST_HOLDING` to the end of the `WAITLIST`.
    3.  Update status to `FINAL_ORDERING`.

### Transition: `FINAL_ORDERING` → `FINISHED`
*   **Trigger**: `current_time >= finished_trigger`
*   **Action**: Update status to `FINISHED`.
```
