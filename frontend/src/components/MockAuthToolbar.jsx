import { useState, useEffect } from 'react'
import { supabase } from '../supabaseClient'
import mockUsers from '../mock_users.json'

const MockAuthToolbar = () => {
    // Only show if VITE_USE_MOCK_AUTH is true
    const useMock = import.meta.env.VITE_USE_MOCK_AUTH === 'true'
    if (!useMock) return null

    const [open, setOpen] = useState(false)
    const [selectedRole, setSelectedRole] = useState('primary')
    const [currentUser, setCurrentUser] = useState(null)

    useEffect(() => {
        // Check current session
        supabase.auth.getSession().then(({ data: { session } }) => {
            if (session?.user) {
                // Try to find in mock users to show name
                const found = mockUsers.find(u => u.id === session.user.id)
                setCurrentUser(found || { name: 'Unknown Mock User' })
            } else {
                setCurrentUser(null)
            }
        })
    }, [])

    const handleLogin = async (user) => {
        // In our Mock Supabase Client, signInWithOAuth is intercepted.
        // But here we want to force a specific user.
        // We can use a custom method exposed by our mock client or just leverage local storage hack
        // if we updated supabaseClient.js to read from it.

        // BETTER: Let's assume supabaseClient.js has a method `signInAsMockUser(user)` 
        // OR we just set localStorage and reload, letting supabaseClient.js pick it up on init.

        localStorage.setItem('mock_auth_user', JSON.stringify(user))
        window.location.reload()
    }

    const handleLogout = async () => {
        localStorage.removeItem('mock_auth_user')
        await supabase.auth.signOut()
        window.location.reload()
    }

    const filteredUsers = mockUsers.filter(u => u.role === selectedRole)

    return (
        <div style={{
            position: 'fixed',
            bottom: '10px',
            left: '10px',
            backgroundColor: '#333',
            color: 'white',
            padding: '10px',
            borderRadius: '5px',
            zIndex: 9999,
            fontSize: '12px',
            fontFamily: 'monospace'
        }}>
            <div style={{ marginBottom: '5px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                <strong>🛠 Mock Auth</strong>
                <button onClick={() => setOpen(!open)} style={{ marginLeft: 'auto' }}>
                    {open ? '▼' : '▲'}
                </button>
            </div>

            {open && (
                <div>
                    <div style={{ marginBottom: '10px', borderBottom: '1px solid #555', paddingBottom: '5px' }}>
                        Current: <strong>{currentUser ? currentUser.name : 'Guest (Not Logged In)'}</strong>
                        {currentUser && (
                            <button onClick={handleLogout} style={{ marginLeft: '10px', color: '#ff6b6b' }}>
                                Logout
                            </button>
                        )}
                    </div>

                    <div style={{ marginBottom: '5px' }}>
                        <select
                            value={selectedRole}
                            onChange={e => setSelectedRole(e.target.value)}
                            style={{ width: '100%', marginBottom: '5px', padding: '2px' }}
                        >
                            <option value="primary">Primary Users</option>
                            <option value="secondary">Secondary Users</option>
                            <option value="guest">Verified Guests</option>
                            <option value="admin">Admins</option>
                        </select>
                    </div>

                    <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                        {filteredUsers.map(user => (
                            <button
                                key={user.id}
                                onClick={() => handleLogin(user)}
                                style={{
                                    display: 'block',
                                    width: '100%',
                                    textAlign: 'left',
                                    padding: '2px 5px',
                                    marginBottom: '2px',
                                    backgroundColor: currentUser?.id === user.id ? '#4caf50' : '#444',
                                    border: 'none',
                                    color: 'white',
                                    cursor: 'pointer'
                                }}
                            >
                                {user.name} ({user.email})
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}

export default MockAuthToolbar
