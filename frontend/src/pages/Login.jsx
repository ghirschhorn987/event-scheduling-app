import { useState } from 'react'
import { supabase } from '../supabaseClient'

export default function Login() {
    const [loading, setLoading] = useState(false)

    const handleLogin = async () => {
        setLoading(true)
        const { error } = await supabase.auth.signInWithOAuth({
            provider: 'google',
        })
        if (error) alert(error.message)
        setLoading(false)
    }

    return (
        <div className="login-page">
            <div className="login-card">
                <h1>Welcome Back</h1>
                <p>Sign in to manage your event roster</p>
                <button className="primary-btn" onClick={handleLogin} disabled={loading}>
                    {loading ? 'Connecting...' : 'Sign in with Google'}
                </button>
            </div>
        </div>
    )
}
