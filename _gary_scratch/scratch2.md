On any pages with list of Events , the events should be listed in chronological order, not reverse order, but there should be a filter to hide/show events.  We should be able to filter by whether event is in the past or future.  We should also be able to filter by event status.  The default settings should be to show all future events.  After doing this, change title of "Upcoming Events" to just "Events"

Have Gemini create a manual testing plan for me with exact steps to let me verify that scheduling is fully working as intended.  All features should be tested and the test plan should be laid out such that I can click off things once done.  It should be orderd in a way where most important functionality is tested first.  For instance, out-of-town guest funcationality is low.

Make sure people can remove and add to event if event is in final ordering status. 

Make sure event is not set to finished until after the event start time PLUS the event duration.

The Edit Event Type screen has several fiedls stored in minutes in the database.  That is good, but the UI should display time in hours and minutes and should accept time in hours and minutes.  The labels for these fields currently say "(minutes)" or "(min)" after the field name.  These qualificaiotns should be removed.



Verify if adding guests is correctly adding to right place.  I think I saw I added a guest and it went right to the event instead of the holding list.  

Remove the Toggle Email View button and make email always displayed in the header and in the Event sign up list. 

Add a button to immediately invoke scheduler function

Review or write the emails that will sent out on signup open, schedule confirmation, and late stage changes.

Prepare CSV file for import of users into the system.  Ask Gemini to do it from existing CSV file.

Change hosting to bethamhoops.skeddle.net.

Show on users page if they are using Google authenticaion or own password.

Ask how easy it is for users to know if they used Google or password to sign in.  If not easy, we should add something to the users page to show this.

Ask if usrs can change from Google to password or vice versa.  If not easy, we should add something to the users page to show this.

Have Gemini audit the Supabase audit table, users table, profile table and see if there are any inconsistencies in terms of user having entry in one table that is inconsisent with others.  Also audit if there are any duplicate names or emails

Move "New To The Game" workflow away from normal signup page to a dedicated page or set of pages.  Add explanations to make process less confusing.  

On the normal signup page under the Sign in with Google button make it clear that it is expected to be asked to authencicate with "supabase.com" and that this is normal. Maybe include a link to screen shot?  Maybe say check that url says "google.com"

On Upcoming Events page, make Date more prominient.  Right now, event title is large bold white on left, while day of week, date, and time are smaller and less prominient on the right.  I don't need time ore prominient (though it should still there), but day of week 3 day abbr and actua date (3 day mont abbev) shoud be more prominent

Add a user-friendly help page for non-admins that explains all non-admin functionality from user perspective (not full techncial details).  Including the UI, the event sign up process, and how the signup prioritization/lottery works.

Add an admin help page that goes into more technical depth that explains all functionality. 

Add Cancelled Date screen accepts a date but applies to the event from day before.  Possibly due to a time zone thing?  Can you fix this?

Add filter to Approve Accounts page to show only registration requests with certain statuses.  By default don't show those approved or rejected but show everyone else.  Change "Pending Registration Requests" to just "Registration Requests"

Explain what the different type values mean on the User Groups page. Possibly rename to be clearer -- suggest alternatives but don't rename them.


The Admn Events page should have the same sort order and filters and default settings as the Events page

The main event details has 3 sections name "Signed Up" "Waitlist" and "Holding Area".  These terms should be consistent throught the app but they are not.  IN some places, we use "Roster" instead of "Signed Up", like at the summary at top of event etails page that counts current signups and in the Manage Event Users pages where the different sections are called "Roster", "Waitlist", and "Holding Queue".  Please correct these locations and let me know if there are others.  Note that "Roster" is the correct term for the user group consisting of the people that have priority (e.g. current SundayBasketball group).  Use of roster should not change there nor in the event status enum OPEN_FOR_ROSTER -- that is correct. 

Add functionality for someone to remove their guests from an event.

On the non-Help page, please add information about what the different event status values mean.  

THe list on Manage Event Lists should show the current counts for the different signup lists (signed up, waitlist plus holding queue) for each event.  It csn be simple set of numbers separated by slash, like it is on the Events page.  The waitlist and holding queue should be combined into one count. 








