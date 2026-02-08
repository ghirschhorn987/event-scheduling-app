-- Create the registration_requests table
CREATE TABLE registration_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE, -- Prevent duplicate pending requests? Or just email.
    affiliation TEXT NOT NULL,
    referral TEXT,
    status TEXT NOT NULL CHECK (status IN ('PENDING', 'APPROVED', 'DECLINED', 'INFO_NEEDED')) DEFAULT 'PENDING',
    admin_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Enable RLS
ALTER TABLE registration_requests ENABLE ROW LEVEL SECURITY;

-- Policies

-- 1. Public can INSERT (Request Access) - but only unauthenticated or anon?
-- Actually, we want ANONYMOUS users to be able to insert.
CREATE POLICY "Public can create registration requests" 
ON registration_requests 
FOR INSERT 
WITH CHECK (true);

-- 2. Public can VIEW their own request? 
-- This is hard because they aren't authenticated yet. 
-- We might need a "token" or just rely on email?
-- For now, let's say NO public read access. 
-- The user sees "Request Received" and that's it.
-- If they want to check status, they wait for email.

-- 3. Admins can DO EVERYTHING
-- We need to know who is an admin.
-- We can use the Service Role (which bypasses RLS).
-- OR we can check `profiles.role` or `user_groups`.
-- For now, let's assume the API will use SERVICE_ROLE_KEY to read/update these.
-- So we don't strictly *need* an RLS policy for admins if the API uses Service Role.
-- BUT if we want Frontend Admin Dashboard to read it directly (using authenticated user),
-- we need a policy.

-- Admin Read Policy (Assuming we have a custom claim or we join profiles)
-- Supabase RLS with joins can be slow/complex. 
-- Let's stick to: **API handles Admin logic using Service Role**.
-- So RLS = "Insert Only for Public", "No Select/Update/Delete for Public".

-- If we want to allow "Admins" to read via Frontend Client (Auth User),
-- we need a policy like:
-- `auth.uid() IN (SELECT id FROM profiles WHERE user_group_id = '...admin_group_id...')`
-- This is often discouraged for performance. 
-- BETTER: The `/api/admin/requests` endpoint serves this data.
