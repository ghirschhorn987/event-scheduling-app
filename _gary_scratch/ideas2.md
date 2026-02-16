# Project Plan: Sports Event Scheduling Application

This plan organizes the required tasks into logical phases, ranging from infrastructure updates to frontend feature implementation.

### **Phase 1: Infrastructure & Data Model Updates**

* **Google Workspace Upgrade:** Purchase the lowest-tier "Business Plan" for Google Workspace to enable API access for Google Groups integration.  
* **Database Schema Enhancements:**  
  * **Event Duration:** Remove "Duration" field from “*Event” table* and add it to the *Event Type* table.  Update all code that references Duration in Event to use Event Type instead.  
  * **User Group Types:** Create a "User Group Type" field with the following values:  
    * *Event Eligibility*  
    * *Application Role*  
    * *User Characteristic*  
    * *Other*  
  * **Guest Permissions:** Add specific attributes to User Groups (specifically those marked as *Event Eligibility*), such as an enum or integer for the **"Ability to add out-of-town guests"** (e.g., allowing 0-10 guests).

### **Phase 2: User & Group Management**

* **New Group Creation:** Create three new User Groups (and corresponding Google Groups) for reserves:  
  * **Sunday Reserves**  
  * **Tuesday Reserves**  
  * **Thursday Reserves**  
* **Sync Logic Implementation:**  
  * Develop a function to read users from a Supabase User Group ("ground truth") and sync them to the associated Google Group.  
  * Create a mechanism to identify discrepancies between the systems.  
  * *(Optional)* Create a reverse-sync function where the Google Group updates the User Group.  
* **Admin Interface:** Add a button to the User Groups admin page to manually trigger the sync function.

### **Phase 3: Event Lifecycle & Scheduling Logic**

* **Status Logic Definition:** Formalize event statuses to flow in this specific order:  
  1. *Not Open*  
  2. *Open for Roster*  
  3. *Open for Reserves*  
  4. *Initially Scheduled (Visitors)*  
  5. *Final Schedule*  
  6. *Closed/Done*  
* **Automated Event Generation:**  
  * Create a generator that ensures events are created **two weeks in advance**.  
  * **Blackout Dates:** Implement logic to read a list of "Canceled Dates" provided by the admin. If a target date matches this list, the system should generate the event with a "Canceled" status immediately.  
* **Automated Status Updates:**  
  * Implement logic to automatically mark an event as **"Closed"** once the time equals *Start Time \+ Duration*.  
* **Documentation:** Produce a technical explanation of how the current scheduler works, specifically regarding status changes, execution frequency, and logic.

### **Phase 4: Notification System (Email Triggers)**

* **Signup Open Notifications:**  
  * **Roster Opening:** Email the specific *Roster* Google Group (e.g., Tuesday Basketball) when their signup window opens.  
  * **Reserve Opening:** Email the specific *Reserve* Google Group when their window opens.  
* **Schedule Confirmation Notifications:**  
  * **Initial Schedule:** Email the *Roster Group* \+ *individual reserves* who signed up (do not email the whole Reserve group).  
  * **Final Schedule:** Email the *Roster Group* \+ *individual sign-ups* with the final order. Include a reminder to remove themselves if they cannot play.  
* **Late-Stage Change Notifications:**  
  * **Trigger:** Occurs between the *Final Schedule* and the *Event Start*.  
  * **Audience:** Email **everyone** involved in the event (roster, reserves, and waitlist) if a user drops out or a status changes.  
  * **Content:** Highlight exactly who dropped out and who is now "in" the game (promoted from the waitlist), requesting confirmation from the new player.

### **Phase 5: Admin Tools & Frontend Features**

* **Event Management Screen:** Build a new admin screen to list all events.  
  * Allow manual cancellation of events.  
  * Allow manual overriding of event statuses (including "un-canceling").  
  * Provide an interface to input the list of "Canceled Dates" used by the generator.  
* **Out-of-Town Guest Feature:**  
  * **UI:** Add an "Add Out-of-Town Guest" button for eligible users (determined by their User Group settings).  
  * **Logic:** Allow users to add a specific number of guests (e.g., 0-10). These guests should be placed at the **top of the holding/waitlist**.  
  * **Backend:** Design a solution for "dummy profiles" or placeholders to represent these guests in the event list without requiring full user accounts.
