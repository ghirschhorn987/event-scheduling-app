import { useState } from 'react'
import { supabase } from '../../supabaseClient'
import { Link, useNavigate } from 'react-router-dom'

export default function Login() {
    const [loading, setLoading] = useState(false)
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [message, setMessage] = useState('')
    const navigate = useNavigate()

    const handleGoogleLogin = async () => {
        setLoading(true)
        const { error } = await supabase.auth.signInWithOAuth({
            provider: 'google',
            options: {
                redirectTo: `${window.location.origin}/dashboard`
            }
        })
        if (error) setMessage(error.message)
        setLoading(false)
    }

    const handleLogin = async (e) => {
        e.preventDefault()
        setLoading(true)
        setMessage('')

        const { error } = await supabase.auth.signInWithPassword({
            email,
            password
        })

        if (error) {
            setMessage(error.message)
        } else {
            // Successful login will trigger session change in App.jsx and redirect
            navigate('/dashboard')
        }
        setLoading(false)
    }

    return (
        <div className="login-card">
            <h1>Welcome Back</h1>
            <p>Sign in to manage your event roster</p>

            <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="input-field"
                />

                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="input-field"
                />

                <button className="primary-btn" type="submit" disabled={loading}>
                    {loading ? 'Signing In...' : 'Sign In'}
                </button>
            </form>

            <div className="divider">or</div>

            <button className="secondary-btn" onClick={handleGoogleLogin} disabled={loading} style={{ width: '100%' }}>
                Sign in with Google
            </button>

            {import.meta.env.VITE_USE_MOCK_AUTH === 'true' && (
                <button
                    className="primary-btn"
                    onClick={async () => {
                        setLoading(true)
                        const { error } = await supabase.auth.signInWithOAuth({ provider: 'mock' })
                        if (error) setMessage(error.message)
                        setLoading(false)
                        // Mock auth doesn't auto-redirect in some implementations if not using onAuthStateChange properly in component
                        // But App.jsx listens to state change, so it should redirect.
                    }}
                    disabled={loading}
                    style={{ width: '100%', marginTop: '1rem', backgroundColor: '#ec4899' }}
                >
                    Guest Login (Mock)
                </button>
            )}

            <div className="auth-links">
                <p>Don't have an account? <Link to="/signup">Sign Up</Link></p>
                <p><Link to="/forgot-password">Forgot Password?</Link></p>
            </div>

            {message && <p style={{ marginTop: '1rem', color: 'red' }}>{message}</p>}
        </div>
    )
}
