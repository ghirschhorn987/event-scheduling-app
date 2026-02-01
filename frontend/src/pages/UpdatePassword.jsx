import { useState, useEffect } from 'react'
import { supabase } from '../supabaseClient'
import { useNavigate } from 'react-router-dom'

export default function UpdatePassword() {
    const [password, setPassword] = useState('')
    const [loading, setLoading] = useState(false)
    const [message, setMessage] = useState('')
    const navigate = useNavigate()

    useEffect(() => {
        // Only allow access if we have a session (handled by auto-login from link)
        supabase.auth.getSession().then(({ data: { session } }) => {
            if (!session) {
                // If checking via email link, the hash usually logs them in automatically.
                // If not, they might need to re-request.
                setMessage("No active session. Please click the reset link in your email again.")
            }
        })
    }, [])

    const handleUpdate = async (e) => {
        e.preventDefault()
        setLoading(true)
        setMessage('')

        const { error } = await supabase.auth.updateUser({
            password: password
        })

        if (error) {
            setMessage('Error: ' + error.message)
        } else {
            setMessage('Password updated successfully! Redirecting...')
            setTimeout(() => navigate('/dashboard'), 2000)
        }
        setLoading(false)
    }

    return (
        <div className="login-page">
            <div className="login-card">
                <h1>Reset Password</h1>
                <p>Enter your new password below.</p>

                <form onSubmit={handleUpdate}>
                    <div style={{ marginBottom: '1rem' }}>
                        <input
                            type="password"
                            placeholder="New Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            style={{ width: '100%', padding: '0.5rem' }}
                        />
                    </div>
                    <button className="primary-btn" type="submit" disabled={loading || !password}>
                        {loading ? 'Updating...' : 'Update Password'}
                    </button>
                </form>
                {message && <p style={{ marginTop: '1rem', color: message.includes('Error') ? 'red' : 'green' }}>{message}</p>}
            </div>
        </div>
    )
}
