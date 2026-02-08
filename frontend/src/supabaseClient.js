import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
    console.warn("Supabase credentials missing! Please set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in .env")
}

const realSupabase = createClient(
    supabaseUrl || 'https://placeholder.supabase.co',
    supabaseAnonKey || 'placeholder'
)

const useMock = import.meta.env.VITE_USE_MOCK_AUTH === 'true'

// -- MOCK AUTH STATE --
// Read from LocalStorage set by MockAuthToolbar
const storedMockUser = typeof window !== 'undefined' ? localStorage.getItem('mock_auth_user') : null
const activeMockUser = storedMockUser ? JSON.parse(storedMockUser) : null

const mockSession = activeMockUser ? {
    user: {
        id: activeMockUser.id,
        email: activeMockUser.email,
        app_metadata: {},
        user_metadata: { full_name: activeMockUser.name },
        aud: 'authenticated',
        created_at: new Date().toISOString()
    },
    // Backend expects: mock-token-{id} or similar. 
    // Backend Logic: `token.startswith("mock-token-")` -> `user_id = token.replace("mock-token-", "")`
    // So if ID is UUID, token should be `mock-token-UUID`.
    access_token: `mock-token-${activeMockUser.id}`,
    expires_in: 3600,
    refresh_token: 'mock-refresh',
    token_type: 'bearer'
} : null

// Mock Profiles are now in DB, so we don't need hardcoded mocks here.
// But we might want to ensure 'from(profiles)' returns something if RLS blocks us?
// No, the whole point is we use REAL DB. 
// BUT: Backend uses SERVICE KEY to create them. Frontend using 'anon' key might face RLS
// if RLS relies on auth.uid().
// If `mockSession.user.id` matches the real UUID in DB, and RLS says `auth.uid() = id`,
// AND Supabase Client "auth" sends this fake token...
// WAIT. Supabase Client sends the token to Supabase. Supabase verifies it.
// Supabase will REJECT `mock-token-...` as invalid JWT!

// CRITICAL FINDING:
// If we use `createClient(url, key)`... normal queries go to Supabase.
// Supabase will inspect the `Authorization` header.
// If it's "mock-token-...", Supabase will say 401 Invalid Token.

// SOLUTION:
// We must intercept network requests or at least PROFILE queries?
// OR: We rely on the FACT that our Backend is where we do complex stuff.
// Frontend usage of `supabase.from(...)`:
// 1. `Dashboard.jsx` calls `fetch('/api/signup')`. This goes to OUR Backend. OUR Backend verifies mock token. OK.
// 2. `Dashboard.jsx` calls `supabase.from('events').select(...)`. 
//    - Events are public (RLS: true). "mock-token" might cause 400?
//    - Authenticated users usually send a valid JWT.
//    - If we send garbage, Supabase might error or treat as Anon.
//    - If `events` table is public, Anon is fine.
//    - BUT `profiles` is RLS `auth.uid() = id`. 
//    - We CANNOT query `profiles` from Frontend with a Mock Token against Real Supabase.

// REVISED STRATEGY for Frontend Data:
// The `mock_auth_strategy` says: "Simulate Authentication".
// If we want Frontend to query `profiles`, we HAVE to mock the response in `supabaseClient.js`.
// WE CAN use `activeMockUser` to mock the `from('profiles').select().eq('id', user.id)` response!

const activeMockProfile = activeMockUser ? {
    id: activeMockUser.id,
    name: activeMockUser.name,
    email: activeMockUser.email,
    user_group_id: activeMockUser.role === 'primary' ? 'primary-group-uuid' :
        activeMockUser.role === 'secondary' ? 'secondary-group-uuid' : null
    // Note: Group UUIDs are not known here easily unless we hardcode or fetch. 
    // For now, let's return basic profile. 
    // The Toolbar JSON has 'role'. We can map that to a fake group ID or just trust the backend.
} : null

// -- MOCK AUTH STATE MANAGEMENT --
const authSubscribers = new Set();

export const supabase = useMock ? {
    ...realSupabase,
    auth: {
        ...realSupabase.auth,
        getSession: async () => {
            return { data: { session: mockSession }, error: null }
        },
        onAuthStateChange: (callback) => {
            if (mockSession) {
                callback('SIGNED_IN', mockSession)
            } else {
                callback('SIGNED_OUT', null)
            }
            return { data: { subscription: { unsubscribe: () => { } } } }
        },
        signInWithOAuth: async () => {
            // Block OAuth in mock mode
            alert("In Mock Mode, use the Toolbar to login!")
            return { error: { message: "Mock Mode Enabled" } }
        },
        signOut: async () => {
            localStorage.removeItem('mock_auth_user')
            window.location.reload()
            return { error: null }
        }
    },
    from: (table) => {
        if (table === 'profiles') {
            return {
                select: (columns) => {
                    return {
                        eq: (col, val) => {
                            if (col === 'id' && activeMockUser && val === activeMockUser.id) {
                                return {
                                    single: async () => ({ data: activeMockProfile, error: null }),
                                    then: (cb) => cb({ data: [activeMockProfile], error: null })
                                }
                            }
                            return { single: async () => ({ data: null, error: { message: 'Not found' } }) }
                        }
                    }
                }
            }
        }
        // For 'events' and 'event_signups', we want REAL data.
        // BUT if we send 'mock-token' to Supabase, it will fail 401.
        // We need to use the ANON key (public access) for these queries.
        // `realSupabase` instance is already using Anon Key.
        // However, `realSupabase` might attach the session token if set? 
        // No, `realSupabase` manages its own session. If we don't call `realSupabase.auth.signIn`, it stays Anon.
        // Since we are mocking `auth`, `realSupabase` considers itself logged out (Anon).
        // So queries to `events` (public) will work as Anon.
        // Queries to `event_signups` (public read) will work as Anon.
        // Inserts to `event_signups`? 
        // Frontend DOES NOT insert to `event_signups` directly anymore! It calls `/api/signup`.
        // So we are safe!
        return realSupabase.from(table)
    }
} : realSupabase
