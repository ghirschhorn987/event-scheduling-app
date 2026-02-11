import { useState, useEffect } from 'react'
import { supabase } from '../supabaseClient'
import mockUsers from '../mock_users.json'

const MockAuthToolbar = () => {
    // Only show if VITE_USE_MOCK_AUTH is true
    const useMock = import.meta.env.VITE_USE_MOCK_AUTH === 'true'
    if (!useMock) return null

    const [open, setOpen] = useState(false)
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

    // const filteredUsers = mockUsers.filter(u => u.role === selectedRole)

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
            fontFamily: 'monospace',
            maxHeight: '400px',
            display: 'flex',
            flexDirection: 'column'
        }}>
            <div style={{ marginBottom: '5px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                <strong>🛠 Mock Auth</strong>
                <button onClick={() => setOpen(!open)} style={{ marginLeft: 'auto', cursor: 'pointer' }}>
                    {open ? '▼' : '▲'}
                </button>
            </div>

            {open && (
                <div style={{ overflowY: 'auto' }}>
                    <div style={{ marginBottom: '10px', borderBottom: '1px solid #555', paddingBottom: '5px' }}>
                        Current: <strong>{currentUser ? currentUser.name : 'Guest (Not Logged In)'}</strong>
                        {currentUser && (
                            <button onClick={handleLogout} style={{ marginLeft: '10px', color: '#ff6b6b', cursor: 'pointer' }}>
                                Logout
                            </button>
                        )}
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                        {mockUsers.map(user => (
                            <button
                                key={user.id}
                                onClick={() => handleLogin(user)}
                                style={{
                                    display: 'block',
                                    width: '100%',
                                    textAlign: 'left',
                                    padding: '4px 8px',
                                    backgroundColor: currentUser?.id === user.id ? '#4caf50' : '#444',
                                    border: 'none',
                                    color: 'white',
                                    cursor: 'pointer',
                                    borderRadius: '3px'
                                }}
                            >
                                <div><strong>{user.name}</strong></div>
                                <div style={{ fontSize: '10px', opacity: 0.8 }}>
                                    {user.email}
                                </div>
                                {user.groups && user.groups.length > 0 && (
                                    <div style={{ fontSize: '10px', color: '#81c784' }}>
                                        [{user.groups.join(', ')}]
                                    </div>
                                )}
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}

export default MockAuthToolbar
