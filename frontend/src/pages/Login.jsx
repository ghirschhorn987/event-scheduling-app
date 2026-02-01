import { useState } from 'react'
import { supabase } from '../supabaseClient'

export default function Login() {
    const [loading, setLoading] = useState(false)
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [mode, setMode] = useState('LOGIN') // LOGIN, SIGNUP, FORGOT
    const [message, setMessage] = useState('')

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

    const handleEmailAuth = async (e) => {
        e.preventDefault()
        setLoading(true)
        setMessage('')

        let result
        if (mode === 'LOGIN') {
            result = await supabase.auth.signInWithPassword({ email, password })
        } else if (mode === 'SIGNUP') {
            result = await supabase.auth.signUp({
                email,
                password,
                options: {
                    emailRedirectTo: `${window.location.origin}/dashboard`
                }
            })
            if (!result.error && result.data.user && !result.data.session) {
                setMessage('Check your email for the confirmation link!')
                setLoading(false)
                return
            }
        } else if (mode === 'FORGOT') {
            result = await supabase.auth.resetPasswordForEmail(email, {
                redirectTo: `${window.location.origin}/update-password`,
            })
            if (!result.error) {
                setMessage('Password reset email sent!')
                setLoading(false)
                return
            }
        }

        const { error } = result
        if (error) setMessage(error.message)
        setLoading(false)
    }

    return (
        <div className="login-page">
            <div className="login-card">
                <h1>{mode === 'FORGOT' ? 'Reset Password' : 'Welcome Back'}</h1>
                <p>
                    {mode === 'FORGOT'
                        ? 'Enter your email to receive a reset link'
                        : 'Sign in to manage your event roster'}
                </p>

                {/* Main Form */}
                <form onSubmit={handleEmailAuth} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <input
                        type="email"
                        placeholder="Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        className="input-field"
                    />

                    {mode !== 'FORGOT' && (
                        <input
                            type="password"
                            placeholder="Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            className="input-field"
                        />
                    )}

                    <button className="primary-btn" type="submit" disabled={loading}>
                        {loading ? 'Processing...' : (mode === 'LOGIN' ? 'Sign In' : (mode === 'SIGNUP' ? 'Sign Up' : 'Send Reset Link'))}
                    </button>
                </form>

                {/* Google Button */}
                {mode !== 'FORGOT' && (
                    <>
                        <div className="divider">or</div>
                        <button className="secondary-btn" onClick={handleGoogleLogin} disabled={loading}>
                            Sign in with Google
                        </button>
                    </>
                )}

                {/* Toggles */}
                <div style={{ marginTop: '1rem', fontSize: '0.9rem' }}>
                    {mode === 'LOGIN' && (
                        <>
                            <p>Don't have an account? <a href="#" onClick={() => setMode('SIGNUP')}>Sign Up</a></p>
                            <p><a href="#" onClick={() => setMode('FORGOT')}>Forgot Password?</a></p>
                        </>
                    )}
                    {mode === 'SIGNUP' && (
                        <p>Already have an account? <a href="#" onClick={() => setMode('LOGIN')}>Sign In</a></p>
                    )}
                    {mode === 'FORGOT' && (
                        <p><a href="#" onClick={() => setMode('LOGIN')}>Back to Login</a></p>
                    )}
                </div>

                {message && <p style={{ marginTop: '1rem', color: message.includes('Check') || message.includes('sent') ? 'green' : 'red' }}>{message}</p>}
            </div>

            <style>{`
                .input-field { padding: 0.75rem; border: 1px solid #ccc; border-radius: 4px; }
                .divider { text-align: center; margin: 1rem 0; color: #888; font-size: 0.8rem; }
                a { color: #2563eb; text-decoration: none; cursor: pointer; }
                a:hover { text-decoration: underline; }
            `}</style>
        </div>
    )
}
