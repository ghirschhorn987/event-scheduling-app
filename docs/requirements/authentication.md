# Authentication & Registration System Requirements

## Overview
The application will implement a **"Invite/Approval-First"** registration flow. Users cannot simply sign up and access the application; they must request access, be approved by an administrator, and then "claim" their pre-created profile.

## User Roles
*   **Administrator**: Can review requests and manage users.
*   **Standard Users**:
    *   **Primary**
    *   **Legacy Primary**
    *   **Secondary**
*   **Unauthenticated**: Can only view Login and Registration Request pages.

## Workflow 1: Registration Request
**Actor**: Visitor (Unauthenticated)

1.  User visits the application.
2.  If not logged in, they are redirected to a **Login Page**.
3.  Login Page contains a link: *"Request to Join"*.
4.  User clicks link and sees a **Registration Form**.
    *   **Fields**:
        *   Full Name
        *   Email Address
        *   **Affiliation**: "Are you affiliated with Temple Beth Am or Pressman? If so, what is the affiliation (e.g. Beth Am Member, Pressman Parent, Pressman Alumni, Staff)"
        *   **Referral**: "If not a member, who referred you to the game?"
5.  User submits form.
6.  **System Action**:
    *   Creates a `registration_requests` record in the database.
    *   Sends an **email to Administrators** notification of a new request.
    *   Displays a "Request Received" message to the User.

## Workflow 2: Admin Review
**Actor**: Administrator

1.  Admin logs in and navigates to the **Administration Dashboard**.
2.  Admin views a list of pending **Registration Requests**.
3.  Admin selects a request and chooses an action:

    ### Option A: Approve
    *   Admin selects a **Role** (Administrator, Primary, Legacy Primary, Secondary).
    *   **System Action**:
        1.  Creates a record in the `profiles` table with the user's Name, Email, and Role.
            *   *Note*: The `auth_user_id` (foreign key to Supabase Auth) is initially `NULL`.
        2.  Sends an **Approval Email** to the user containing a link to the Login page.

    ### Option B: Decline
    *   Admin enters a reason.
    *   **System Action**:
        *   Updates request status to 'Declined'.
        *   Sends a **Rejection Email** to the user with the provided reason.

    ### Option C: Request Info
    *   Admin enters a question/comment.
    *   **System Action**:
        *   Sends an email to the user requesting more information.

## Workflow 3: User Onboarding (Claiming Profile)
**Actor**: Approved User

1.  User receives **Approval Email** and clicks the link to return to the app.
2.  User chooses a Sign-Up method via **Supabase Auth**:
    *   Google OAuth
    *   Email & Password
3.  **System Action (Critical)**:
    *   Upon successful authentication, a **Post-User-Creation Trigger** (or API logic) runs.
    *   It checks the `profiles` table for a record matching the user's **Email Address**.
    *   **If found**: It updates the `profiles` record, linking it to the new Supabase `auth.uid`.
    *   **If not found**: Access is denied (or treated as a basic guest without a role).
4.  User is granted access to the app based on the Role assigned in their Profile.

## Key Technical Requirements
1.  **Public Access Control**: Middleware/RLS must ensure `profiles` and app data are not accessible without a valid session.
2.  **Profile Linking**: The system must verify that the email used to Sign Up matches the email approved by the Admin.
3.  **Password Reset**: Standard Supabase functionality.

---

## Open Questions [RESOLVED]
1.  **Registration Questions**: 
    - Name
    - Email
    - Affiliation (Temple Beth Am/Pressman details)
    - Referral source (if not a member)
2.  **Request Storage**: Requests will be stored in a database table (`registration_requests`) for persistence and admin management.
3.  **Role Permissions**: 
    - **Administrator**: Full app permissions.
    - **Primary / Legacy Primary / Secondary**: Currently have same app permissions as standard users, but will be used for **scheduling prioritization logic** in automatic functions.
