# Domain Migration Plan: skeddle.club -> bethamhoops.skeddle.net

## 1. Domain Registration & DNS Hosting (Cloudflare)
Since your domain name is managed in Cloudflare:
- Go to the **skeddle.net** zone in Cloudflare.
- **Add a CNAME / A Record**: Point `bethamhoops.skeddle.net` to your Google Cloud Run custom domain mapping (or Firebase Hosting, wherever your frontend resides).
- **Set up Domain Verification for Resend**: You will need to add TXT and MX records in Cloudflare for `skeddle.net` to authorize Resend to send emails on your behalf.
- *(Optional)* Add a Page Rule or Redirect Rule to forward all traffic from `skeddle.club` to `bethamhoops.skeddle.net` to ensure no user gets lost.

## 2. Google Cloud Hosting (Cloud Run)
- Go to the **Cloud Run** console -> **Custom Domains** (or your external Load Balancer, depending on your setup).
- Add the new domain `bethamhoops.skeddle.net` and map it to your frontend service.
- Google Cloud will provide you with DNS records (if it's a new domain mapping). You will need to add these to the `skeddle.net` zone in Cloudflare.
- Update any Environment Variables applied to your Cloud Run instances that reference the old domain (e.g., `VITE_API_URL` or allowed CORS origins).

## 3. Supabase Database
Your authentication flows securely depend on validating where users are logging in from.
- **Authentication -> URL Configuration**: Update the "Site URL" to `https://bethamhoops.skeddle.net`.
- **Authentication -> URL Configuration -> Redirect URLs**: Add `https://bethamhoops.skeddle.net/*` to the list of allowed redirect URLs. (You can keep `skeddle.club` temporarily during migration).
- **Google Auth Provider**: No changes needed *inside* Supabase if using `signInWithOAuth`, as the Supabase callback URL (`https://<PROJECT_REF>.supabase.co/auth/v1/callback`) handles the transaction and won't change.
- **Email Templates**: If you have customized any email templates in Supabase (Authentication -> Email Templates), update any hardcoded links to point to the new domain.

## 4. Email Sender (Resend)
- In your Resend console, add the new domain **skeddle.net** (or `bethamhoops.skeddle.net`).
- Resend will generate a set of DNS records (DKIM, SPF, etc). Add these to Cloudflare to verify the domain.
- Once verified, you will be able to send transactional app emails using your new sender email (e.g., `support@skeddle.net`).

## 5. Google Workspace (ghirschhorn@skeddle.net)
- **Email Aliases**: Since you likely want user support emails sent from the app to arrive in your inbox, go to your Google Workspace Admin Console and add `support` as an email alias to your `ghirschhorn@skeddle.net` account (or create a Google Group for `support@skeddle.net` that forwards to you).
- **Google Cloud Console (OAuth Credentials)**: Wait, you created OAuth credentials to let users sign in with Google for your app. Go to the Google Cloud Console for the project attached to your Google Workspace:
  - Find the OAuth 2.0 Client ID used for the application.
  - Under "Authorized JavaScript origins", add `https://bethamhoops.skeddle.net`. (The Authorized redirect URIs should already be pointing to your Supabase project URL, which does not need to change).

## 6. Codebase Updates (Local Project)
I searched your local project for references to `skeddle.club`. The following files will need to be updated to use the new domain and support email address:

- **`backend/email_service.py`**:
  - Update the "from" address: `"from": "Skeddle <support@skeddle.club>"` to `"Skeddle <support@skeddle.net>"`.
  - Update all references to `https://skeddle.club` in the HTML body templates to `https://bethamhoops.skeddle.net`.
  - Update the contact email `support@skeddle.club` to `support@skeddle.net` in the email text.
- **`frontend/src/components/Auth/Login.jsx`**:
  - Update the support contact email (`support@skeddle.club` -> `support@skeddle.net`) shown to users when access is denied.
- **`frontend/src/pages/AdminGroupDetail.jsx`**:
  - Fix the instruction text: `Group admins should use the email address listed here to log in to skeddle.club` -> `bethamhoops.skeddle.net`.
- **`database/create_test_user.sql`** & **`frontend/src/mock_users.json`**:
  - Optionally, change test user emails from `@skeddle.club` to `@skeddle.net` for consistency.
