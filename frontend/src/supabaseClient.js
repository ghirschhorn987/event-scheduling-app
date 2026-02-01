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

// -- MOCK AUTH IMPLEMENTATION --
const useMock = import.meta.env.VITE_USE_MOCK_AUTH === 'true'

const mockSession = {
    user: {
        id: 'mock-user-id-123',
        email: 'mock.guest@example.com',
        app_metadata: {},
        user_metadata: { full_name: 'Mock Guest' },
        aud: 'authenticated',
        created_at: new Date().toISOString()
    },
    access_token: 'mock-token',
    expires_in: 3600,
    refresh_token: 'mock-refresh',
    token_type: 'bearer'
}

// Mock Profile for Guest (user_group_id is null)
const mockProfileGuest = {
    id: 'mock-user-id-123',
    name: 'Mock Guest',
    email: 'mock.guest@example.com',
    user_group_id: null, // GUEST
    user_groups: null
}

const mockProfileMember = {
    id: 'mock-user-id-123',
    name: 'Mock Principal',
    email: 'mock.member@example.com',
    user_group_id: '00000000-0000-0000-0000-000000000000', // Fake ID
    user_groups: { id: '00000000-0000-0000-0000-000000000000', name: 'Basketball Regulars' }
}

// Toggle this or control via env if needed. Default to Guest for now.
const activeMockProfile = mockProfileGuest

export const supabase = useMock ? {
    ...realSupabase,
    auth: {
        ...realSupabase.auth,
        getSession: async () => {
            return { data: { session: mockSession }, error: null }
        },
        onAuthStateChange: (callback) => {
            callback('SIGNED_IN', mockSession)
            return { data: { subscription: { unsubscribe: () => { } } } }
        },
        signInWithOAuth: async () => {
            return { data: { session: mockSession }, error: null }
        },
        signOut: async () => {
            return { error: null }
        }
    },
    from: (table) => {
        if (table === 'profiles') {
            return {
                select: (columns) => {
                    return {
                        eq: (col, val) => {
                            if (col === 'id' && val === mockSession.user.id) {
                                return {
                                    single: async () => ({ data: activeMockProfile, error: null }),
                                    // Handle list return if code doesn't use single()
                                    then: (cb) => cb({ data: [activeMockProfile], error: null })
                                }
                            }
                            // Fallback for other queries
                            return { single: async () => ({ data: null, error: { message: 'Not found' } }) }
                        }
                    }
                }
            }
        }
        // Pass through for Events/Signups (we want real event data!)
        // BUT intercept inserts to signups if we want to test joining without DB error
        return realSupabase.from(table)
    }
} : realSupabase
