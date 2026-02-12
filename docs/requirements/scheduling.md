```markdown
# Event Scheduling and Waitlist Specification

## User Tiers
1.  **Tier 1 (Paid Roster):** Users on the paid roster for the specific event.
2.  **Tier 2 (FirstPriority Reserve):** Users in the FirstPriority group, excluding those already in Tier 1.
3.  **Tier 3 (SecondPriority Reserve):** Users in the SecondPriority group, excluding those already in Tier 1.

## Sign-up Windows

### Tier 1 (Direct Entry)
*   **Opens:** `roster_sign_up_open_minutes` before event start.
*   **Behavior:** Users are added immediately to the **Event List** (up to `max_signups`) or the **Waitlist** if the event is full.

### Tiers 2 & 3 (Holding List)
*   **Opens:** `reserve_sign_up_open_minutes` before event start.
*   **Behavior:** Users are added to a temporary **Holding List** until the final scheduling phase.

## Scheduling Phases

### 1. Initial Sorting
At `initial_reserve_scheduling_minutes` before event start, the current **Holding List** is sorted:
1.  Tier 2 users are randomized.
2.  Tier 3 users are randomized.
3.  The randomized Tier 2 users are placed before the randomized Tier 3 users.

### 2. Late Holding Period
Between `initial_reserve_scheduling_minutes` and `final_reserve_scheduling_minutes`, any new signups from Tier 2 or Tier 3 are appended to the end of the **Holding List** in the order they sign up.

### 3. Final Processing
At `final_reserve_scheduling_minutes` before event start:
1.  Users on the **Holding List** are moved to the **Event List** in their sorted order until `max_signups` is reached.
2.  Any remaining users on the **Holding List** are moved to the end of the **Waitlist**.
3.  The **Holding List** is deleted.

## Post-Scheduling Behavior
After `final_reserve_scheduling_minutes`, the **Holding List** is inactive. Any user from any tier who signs up is added directly to the **Event List** (if space is available) or the end of the **Waitlist**.
```
