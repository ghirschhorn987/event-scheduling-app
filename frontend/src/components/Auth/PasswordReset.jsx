import { useState } from 'react'
import { supabase } from '../../supabaseClient'
import { Link } from 'react-router-dom'

export default function PasswordReset() {
    const [loading, setLoading] = useState(false)
    const [email, setEmail] = useState('')
    const [message, setMessage] = useState('')
    const [success, setSuccess] = useState(false)

    const handleReset = async (e) => {
        e.preventDefault()
        setLoading(true)
        setMessage('')

        const { error } = await supabase.auth.resetPasswordForEmail(email, {
            redirectTo: `${window.location.origin}/update-password`,
        })

        if (error) {
            setMessage(error.message)
        } else {
            setSuccess(true)
            setMessage('Password reset email sent! Check your inbox.')
        }
        setLoading(false)
    }

    return (
        <div className="login-card">
            <h1>Reset Password</h1>
            <p>Enter your email to receive a reset link</p>

            {success ? (
                <div className="alert">
                    <p>{message}</p>
                    <p style={{ marginTop: '1rem' }}><Link to="/login">Back to Login</Link></p>
                </div>
            ) : (
                <>
                    <form onSubmit={handleReset} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        <input
                            type="email"
                            placeholder="Email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            className="input-field"
                        />

                        <button className="primary-btn" type="submit" disabled={loading}>
                            {loading ? 'Sending Link...' : 'Send Reset Link'}
                        </button>
                    </form>

                    <div className="auth-links">
                        <p><Link to="/login">Back to Login</Link></p>
                    </div>

                    {message && <p style={{ marginTop: '1rem', color: 'red' }}>{message}</p>}
                </>
            )}
        </div>
    )
}
