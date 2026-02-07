import { useState } from 'react'
import { supabase } from '../../supabaseClient'
import { Link } from 'react-router-dom'

export default function Signup() {
    const [loading, setLoading] = useState(false)
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [message, setMessage] = useState('')
    const [success, setSuccess] = useState(false)

    const handleSignup = async (e) => {
        e.preventDefault()
        setLoading(true)
        setMessage('')

        const { data, error } = await supabase.auth.signUp({
            email,
            password,
            options: {
                emailRedirectTo: `${window.location.origin}/dashboard`
            }
        })

        if (error) {
            setMessage(error.message)
        } else if (data.user && !data.session) {
            setSuccess(true)
            setMessage('Registration successful! Check your email for the confirmation link.')
        } else {
            // Sometimes auto-login happens if email confirmation is off
            setMessage('Registration successful!')
        }
        setLoading(false)
    }

    return (
        <div className="login-card">
            <h1>Create Account</h1>
            <p>Sign up to start scheduling events</p>

            {success ? (
                <div className="alert">
                    <p>{message}</p>
                    <p style={{ marginTop: '1rem' }}><Link to="/login">Back to Login</Link></p>
                </div>
            ) : (
                <>
                    <form onSubmit={handleSignup} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
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
                            minLength={6}
                        />

                        <button className="primary-btn" type="submit" disabled={loading}>
                            {loading ? 'Creating Account...' : 'Sign Up'}
                        </button>
                    </form>

                    <div className="auth-links">
                        <p>Already have an account? <Link to="/login">Sign In</Link></p>
                    </div>

                    {message && <p style={{ marginTop: '1rem', color: 'red' }}>{message}</p>}
                </>
            )}
        </div>
    )
}
