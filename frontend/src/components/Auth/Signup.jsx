import { useState } from 'react'
import { supabase } from '../../supabaseClient'
import { Link } from 'react-router-dom'

export default function Signup() {
    const [loading, setLoading] = useState(false)
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [message, setMessage] = useState('')
    const [success, setSuccess] = useState(false)

    const handleGoogleSignup = async () => {
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
            if (error.message.includes('ACCESS_DENIED') || error.message.includes('rejected by software resource')) {
                setMessage(
                    <span>
                        It looks like you haven't been approved yet.
                        Please <Link to="/request-access" style={{ color: 'inherit', textDecoration: 'underline' }}>Request Access</Link> first.
                        <br /><br />
                        Note: Account creation is only permitted for pre-approved email addresses.
                    </span>
                )
            } else {
                setMessage(error.message)
            }
        } else if (data.user && !data.session) {
            setSuccess(true)
            setMessage('Registration successful! Check your email for the confirmation link.')
        } else {
            setMessage('Registration successful!')
        }
        setLoading(false)
    }

    return (
        <div className="login-card signup-card">
            <h1>Create Account For Approved User</h1>

            <div className="approval-note">
                <span className="icon">⚠️</span>
                <p><strong>Note:</strong> Only pre-approved email addresses can create an account. If you haven't been approved yet, this process will result in an error.</p>
            </div>

            {success ? (
                <div className="alert success-alert">
                    <p>{message}</p>
                    <p style={{ marginTop: '1rem' }}><Link to="/login" className="back-link">Back to Login</Link></p>
                </div>
            ) : (
                <div className="auth-options">
                    {/* Method 1: Password */}
                    <div className="auth-option-section">
                        <div className="option-header">Option 1: Site-Specific Password</div>
                        <p className="option-description">
                            Create a dedicated password for this site. It is encrypted and remains private;
                            the system never sees your actual password. It can't be retrieved, only reset if forgotten.
                        </p>

                        <form onSubmit={handleSignup} className="email-signup-form">
                            <input
                                type="email"
                                placeholder="Email Address"
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
                                {loading ? 'Creating Account...' : 'Create with Password'}
                            </button>
                        </form>
                    </div>

                    <div className="divider">OR</div>

                    {/* Method 2: Google */}
                    <div className="auth-option-section">
                        <div className="option-header">Option 2: Google Authentication</div>
                        <p className="option-description">
                            Use your Google account to sign in securely without creating a new password.
                            Google validates your identity, and the system never sees your credentials.
                        </p>
                        <p className="security-tip">
                            <strong>Note:</strong> You will be redirected to <code>qyeitwnnozvwstxhwhwf.supabase.co</code> for validation.
                            This is our secure database host and is normal.
                        </p>

                        <button className="secondary-btn google-btn" onClick={handleGoogleSignup} disabled={loading}>
                            <img src="/google-icon.svg" alt="" className="google-icon" />
                            Continue with Google
                        </button>
                    </div>

                    <div className="auth-footer">
                        <p>Already have an account? <Link to="/login">Sign In</Link></p>
                    </div>

                    {message && <div className="error-box">{message}</div>}
                </div>
            )}
        </div>
    )
}
