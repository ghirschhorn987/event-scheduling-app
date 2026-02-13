### **Project Plan: Scheduling App Enhancements**

#### **Phase 1: Infrastructure and Data Configuration**
This phase focuses on setting up the necessary user groups, terminology, and external service accounts to support future features.

*   **User Group Setup:**
    *   Create three new User Groups for reserves: "SundayBasketballReserves," "TuesdayBasketballReserves," and "ThursdayBasketballReserves" [3].
*   **Google Workspace Setup:**
    *   Create corresponding Google Groups for the three new Reserve user groups [3].
    *   Upgrade the Google Workspace account to a business plan (lowest tier) that allows API access to Google Groups [4].
    * Update the user groups in database to include the new Google Group ids

#### **Phase 2: Core Application Logic & Statuses**
This phase updates how events are tracked and how the scheduler operates automatically.

*   **Event Status Overhaul:**
    *   Expand the event status list to explicitly track the different stages of signup [5]. The new status flow should be:
        1.  **Not Open:** Not yet open for signups.
        2.  **Open for Roster:** Open specifically for primary roster members.
        3.  **Open for Reserves:** Open for reserve members.
        4.  **Preliminary Ordering:** Preliminary ordering of players with guaranteed spots and a prioritized waitlist.
        5.  **Final Ordering:** Final ordering of players with guaranteed spots and a locked waitlist sequence.
        6.  **Event Finished:** Event is finished.
    *   Ensure these statuses are visible to the user on the game status page [5].
*   **Scheduler Automation:**
    *   Ensure the scheduler runs on a regular basis automatically to trigger status changes [6].
    *   Update logic for the "Post-Final" period (from Final Ordering until Event Finished):
        *   Remove preferences for Roster vs. Reserves; signups become first-come, first-served (added to the end of the list) [7].

#### **Phase 3: Google Groups Integration**
This phase involves backend coding to keep the app's user database in sync with Google Groups.

*   **Sync Logic Development:**
    *   Develop a function to sync Supabase User Groups (ground truth) to Google Groups [8].
        *   Logic: Read users in Supabase group -> Read users in Google Group -> Produce discrepancy list -> Update Google Group to match Supabase.
    *   (Optional) Create a function to sync in the reverse direction (Google Group Master -> Supabase User Group) [8].
*   **Admin Interface:**
    *   Update the "User Groups" page in the Admin screen [2].
    *   Add a button/trigger to manually initiate the sync function for a specific group [2]. Give option to sync in either direction, with default being that Supabase is the ground truth.

#### **Phase 4: Automated Communication (Email Notifications)**
This phase implements a notification system triggered by specific event statuses and user actions.

*   **Signup Window Notifications:**
    *   **Roster Opening:** When an event opens for Roster, send an email to the associated event type Google Group (e.g., Tuesday Basketball) saying "Signup is now open" with a link to the signup page [9].
    *   **Reserve Opening:** When an event opens for Reserves, send an email to the associated event type Reserve Google Group (e.g., Tuesday Basketball Reserves) with a link to the signup page [9].
*   **Schedule Status Notifications:**
    *   **Preliminary Ordering:** When the preliminary ordering is set, email the Roster Google Group AND individual emails of reserves currently signed up [10].
        *   *Content:* The preliminary order is set and a reminder to remove oneself if dropping out.
    *   **Final Ordering:** When the final ordering is set, email the Roster Google Group AND individual emails of people signed up [11].
        *   *Content:* Final order, link to page, and a reminder to remove oneself if dropping out [11].
*   **Dynamic Waitlist/Dropout Notifications:**
    *   **Trigger:** Occurs between "Final Ordering" and the "Event Finished" when someone adds or removes themselves [1].
    *   **Recipients:** Roster Google Group + All individuals currently signed up (active + waitlist + person dropping out) [7].
    *   **Content:**
        *   Current status of who is in the game.
        *   Who is on the waitlist and who is up next.
        *   Who has dropped out.
        *   **Highlight:** Specifically highlight if a user has moved from the waitlist into the active game [12].
    *   **Action Item:** Require users moved from waitlist to active to confirm they are playing (mechanism to be determined, likely in-app confirmation) [12].

#### **Phase 5: Documentation**
*   **Technical Documentation:** Produce an explanation of how the scheduler works, specifically regarding technical operations, run frequency, and how it handles status changes [3].


# Project Plan: Sports Event Scheduling Application

This plan organizes the required tasks into logical phases, ranging from infrastructure updates to frontend feature implementation.

### **Phase 1: Infrastructure & Data Model Updates**
*   **Terminology Refactor:** Conduct a global find-and-replace in the codebase to change the term "Game" to **"Event"** to ensure consistency.
*   **Google Workspace Upgrade:** Purchase the lowest-tier "Business Plan" for Google Workspace to enable API access for Google Groups integration.
*   **Database Schema Enhancements:**
    *   **Event Duration:** Add a "Duration" field to the *Event Type* table.
    *   **User Group Types:** Create a "User Group Type" field with the following values:
        *   *Event Eligibility*
        *   *Application Role*
        *   *User Characteristic*
        *   *Other*
    *   **Guest Permissions:** Add specific attributes to User Groups (specifically those marked as *Event Eligibility*), such as an enum or integer for the **"Ability to add out-of-town guests"** (e.g., allowing 0-10 guests).

### **Phase 2: User & Group Management**
*   **New Group Creation:** Create three new User Groups (and corresponding Google Groups) for reserves:
    *   **Sunday Reserves**
    *   **Tuesday Reserves**
    *   **Thursday Reserves**
*   **Sync Logic Implementation:**
    *   Develop a function to read users from a Supabase User Group ("ground truth") and sync them to the associated Google Group.
    *   Create a mechanism to identify discrepancies between the systems.
    *   *(Optional)* Create a reverse-sync function where the Google Group updates the User Group.
*   **Admin Interface:** Add a button to the User Groups admin page to manually trigger the sync function.

### **Phase 3: Event Lifecycle & Scheduling Logic**
*   **Status Logic Definition:** Formalize event statuses to flow in this specific order:
    1.  *Not Open*
    2.  *Open for Roster*
    3.  *Open for Reserves*
    4.  *Initially Scheduled (Visitors)*
    5.  *Final Schedule*
    6.  *Closed/Done*
*   **Automated Event Generation:**
    *   Create a generator that ensures events are created **two weeks in advance**.
    *   **Blackout Dates:** Implement logic to read a list of "Canceled Dates" provided by the admin. If a target date matches this list, the system should generate the event with a "Canceled" status immediately.
*   **Automated Status Updates:**
    *   Implement logic to automatically mark an event as **"Closed"** once the time equals *Start Time + Duration*.
*   **Documentation:** Produce a technical explanation of how the current scheduler works, specifically regarding status changes, execution frequency, and logic.

### **Phase 4: Notification System (Email Triggers)**
*   **Signup Open Notifications:**
    *   **Roster Opening:** Email the specific *Roster* Google Group (e.g., Tuesday Basketball) when their signup window opens.
    *   **Reserve Opening:** Email the specific *Reserve* Google Group when their window opens.
*   **Schedule Confirmation Notifications:**
    *   **Initial Schedule:** Email the *Roster Group* + *individual reserves* who signed up (do not email the whole Reserve group).
    *   **Final Schedule:** Email the *Roster Group* + *individual sign-ups* with the final order. Include a reminder to remove themselves if they cannot play.
*   **Late-Stage Change Notifications:**
    *   **Trigger:** Occurs between the *Final Schedule* and the *Event Start*.
    *   **Audience:** Email **everyone** involved in the event (roster, reserves, and waitlist) if a user drops out or a status changes.
    *   **Content:** Highlight exactly who dropped out and who is now "in" the game (promoted from the waitlist), requesting confirmation from the new player.

### **Phase 5: Admin Tools & Frontend Features**
*   **Event Management Screen:** Build a new admin screen to list all events.
    *   Allow manual cancellation of events.
    *   Allow manual overriding of event statuses (including "un-canceling").
    *   Provide an interface to input the list of "Canceled Dates" used by the generator.
*   **Out-of-Town Guest Feature:**
    *   **UI:** Add an "Add Out-of-Town Guest" button for eligible users (determined by their User Group settings).
    *   **Logic:** Allow users to add a specific number of guests (e.g., 0-10). These guests should be placed at the **top of the holding/waitlist**.
    *   **Backend:** Design a solution for "dummy profiles" or placeholders to represent these guests in the event list without requiring full user accounts.
