-- Create table for cancelled dates
CREATE TABLE IF NOT EXISTS cancelled_dates (
    date DATE PRIMARY KEY,
    reason TEXT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add RLS policies (if RLS is enabled, otherwise readable by service role/admin)
ALTER TABLE cancelled_dates ENABLE ROW LEVEL SECURITY;

-- Allow read access to authenticated users (so the scheduler/generator can read it, and admins)
CREATE POLICY "Allow read access for authenticated users" ON cancelled_dates
    FOR SELECT TO authenticated USING (true);

-- Allow all access to service role (and potentially admins via app logic)
-- Note: Supabase service role bypasses RLS, so this is for admin users if they use the anon key
-- But usually admin API uses service role or we rely on app-level check.
-- For now, we'll allow full access to authenticated users because the API restricts write access to Admins.
CREATE POLICY "Allow write access for authenticated users" ON cancelled_dates
    FOR ALL TO authenticated USING (true);
