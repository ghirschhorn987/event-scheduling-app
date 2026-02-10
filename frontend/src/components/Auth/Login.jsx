import { useState, useEffect } from 'react'
import { supabase } from '../../supabaseClient'
import { Link, useNavigate, useLocation } from 'react-router-dom'

export default function Login() {
    const [loading, setLoading] = useState(false)
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [message, setMessage] = useState('')
    const navigate = useNavigate()
    const location = useLocation()

    useEffect(() => {
        const queryParams = new URLSearchParams(location.search)
        const error = queryParams.get('error')
        if (error === 'access_denied') {
            setMessage(
                <span>
                    You must request access before being able to log in. See registration instructions below.
                    <br /><br />
                    If you have already registered but haven't received a response within 48 hours, please contact support at support@skeddle.club.
                </span>
            )
        }
    }, [location])

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

        // Check if they are trying to log in but might be denied access logic is handled in App.jsx mostly,
        // but for email/password we can also do a pre-check or just let App.jsx handle it after sign in.
        // App.jsx will catch the session change and sign them out if they don't have a profile.

        const { error } = await supabase.auth.signInWithPassword({
            email,
            password
        })

        if (error) {
            if (error.message === 'Invalid login credentials') {
                // Check if the user exists in profiles (publicly readable)
                // If they exist, it means they typed the wrong password.
                // If they don't exist, they likely aren't registered.
                const { data: profile } = await supabase
                    .from('profiles')
                    .select('id')
                    .eq('email', email)
                    .maybeSingle()

                if (profile) {
                    setMessage("Invalid password. Please try again.")
                } else {
                    setMessage(
                        <span>
                            You must request access before being able to log in. See registration instructions below.
                            <br /><br />
                            If you have already registered but haven't received a response within 48 hours, please contact support at support@skeddle.club.
                        </span>
                    )
                }
            } else {
                setMessage(error.message)
            }
        } else {
            // Successful login will trigger session change in App.jsx and redirect
            navigate('/dashboard')
        }
        setLoading(false)
    }

    return (
        <div className="login-card">
            <h1>Beth Am Basketball</h1>

            {message && (
                <div className="error-message" style={{
                    backgroundColor: '#ffebee',
                    color: '#c62828',
                    padding: '10px',
                    borderRadius: '4px',
                    marginBottom: '1rem',
                    fontSize: '0.9rem',
                    textAlign: 'left'
                }}>
                    {message}
                </div>
            )}

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
                <div style={{ textAlign: 'center' }}>
                    <Link to="/forgot-password" style={{ color: 'var(--primary)', fontSize: '0.9rem' }}>Forgot Password?</Link>
                </div>
            </form>

            <div className="divider">or</div>

            <button className="secondary-btn" onClick={handleGoogleLogin} disabled={loading} style={{ width: '100%' }}>
                Sign in with Google
            </button>
            <p style={{ fontSize: '0.8rem', color: '#666', marginTop: '5px' }}>
                You will be redirected to our secure authentication partner to sign in.
            </p>

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

            <div className="registration-section">
                <h4>New Here? Join The Game</h4>
                <p>1. <Link to="/request-access">Request Access</Link> to get started.</p>
                <p>2. Once approved, <Link to="/signup">Create Your Account</Link>.</p>
            </div>
        </div>
    )
}
