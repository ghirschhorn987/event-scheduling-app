# Authentication & Registration System Requirements

## Overview
The application implements an **"Invite/Approval-First"** registration flow. Users must request access and be approved by an administrator before they can access the system. 

The system supports **Pre-provisioning**: When an administrator approves a request, a profile is created *before* the user actually signs up. When the user eventually signs up using Supabase Auth (Google or Email), a database trigger automatically links their new authentication record to their pre-provisioned profile based on their email address.

## User Groups
The system uses a **User Group mechanism** to manage permissions. A user can belong to zero or more groups (Many-to-Many relationship).

The standard User Groups are:
*   **SuperAdmin**: Full unrestricted access.
*   **Admin**: Administrative access (currently identical to SuperAdmin).
*   **FirstPriority**: Top-tier scheduling priority.
*   **SecondaryPriority**: Second-tier scheduling priority.
*   **BethAmAffiliated**: Users associated with Temple Beth Am.

## Workflow 1: Registration Request
**Actor**: Visitor (Unauthenticated)

1.  User visits the application and is redirected to the **Login Page**.
2.  User clicks *"Request to Join"* to reach the **Registration Form**.
3.  **Registration Form**:
    *   **Identity**: Full Name and Email Address.
    *   **Affiliation Check**: User indicates if they are affiliated with Temple Beth Am or Pressman Academy.
        *   **If Affiliated**: User selects from specific options (Member, Parent, Alumni, Staff, Other).
        *   **If Not Affiliated**: User provides details on how they found out about the game.
4.  User submits the form.
5.  **System Action**:
    *   Creates a `registration_requests` record.
    *   Sends an **Acknowledgement Email** to the user.
    *   Sends an **Admin Notification Email**.

## Workflow 2: Admin Review
**Actor**: Administrator

1.  Admin navigates to the **Administration Dashboard**.
2.  Admin views pending requests and can take several actions:

    ### Option A: Approve
    *   Admin selects zero or more **User Groups** for the user.
    *   **System Action**:
        1.  Creates a record in the `profiles` table (Pre-provisioning).
        2.  Assigns the selected **User Groups** in the `profile_groups` table.
        3.  Updates request status to 'APPROVED'.
        4.  Sends an **Access Granted Email** with a login link.

    ### Option B: Decline
    *   **Decline (Silent)**: Updates status to 'DECLINED' without notifying the user.
    *   **Decline (Message)**: Admin provides a reason; system sends a **Rejection Email** and updates status to 'DECLINED'.

    ### Option C: Request Info
    *   Admin enters a question; system sends an email to the user requesting more details and updates status to 'INFO_NEEDED'.

## Workflow 3: User Onboarding (Claiming Profile)
**Actor**: Approved User

1.  User clicks the link in their **Access Granted Email**.
2.  User signs up via **Supabase Auth** (Google or Email/Password).
3.  **Security Enforcement (Strict Block)**:
    *   A database trigger (`on_auth_user_created`) runs **before** the signup completes.
    *   The trigger searches the `profiles` table for a record matching the user's email.
    *   **Access Denied**: If no record is found, the trigger raises an exception, and the signup is **rejected**. The user sees a message directing them to request access.
    *   **Link**: If found, it updates the profile with the user's new Supabase `auth_user_id`.
4.  User is granted access based on the groups assigned to their profile.

## Key Technical Requirements
1.  **Public Access**: The `registration_requests` table allows public inserts. All other application data is protected by session-based RLS.
2.  **Profile Linking**: The `email` column in the `profiles` table is unique and serves as the primary link during onboarding.
3.  **Many-to-Many Groups**: User groups are managed via a join table (`profile_groups`).

---

## Open Questions 

