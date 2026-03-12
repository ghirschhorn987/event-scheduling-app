import { useState, useEffect } from 'react'
import { supabase } from '../supabaseClient'
import Header from '../components/Header'

const Profile = ({ session }) => {
    const [profile, setProfile] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (session?.user) {
            fetchProfile()
        }
    }, [session])

    const fetchProfile = async () => {
        setLoading(true)
        try {
            const { data, error } = await supabase
                .from('profiles')
                .select('id, name, email, auth_method')
                .eq('auth_user_id', session.user.id)
                .single()

            if (data) {
                setProfile(data)
            }
        } catch (err) {
            console.error("Error fetching profile:", err)
        } finally {
            setLoading(false)
        }
    }

    if (loading) return <div className="loading-screen">Loading Profile...</div>
    if (!profile) return <div className="p-8 text-center text-white">Profile not found</div>

    return (
        <div className="dashboard-container text-white">
            <Header session={session} />

            <div className="max-w-4xl mx-auto px-4 py-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold">Your Profile</h1>
                    <p className="text-gray-400 mt-2">Manage your account information and authentication settings.</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {/* Profile Details */}
                    <div className="md:col-span-2 space-y-6">
                        <div className="bg-slate-800 rounded-2xl border border-slate-700 shadow-xl overflow-hidden">
                            <div className="p-6 border-b border-slate-700 bg-slate-900/50">
                                <h2 className="text-xl font-bold text-white">Account Information</h2>
                            </div>
                            <div className="p-6 space-y-4">
                                <div>
                                    <label className="text-xs text-gray-500 font-bold uppercase tracking-widest">Display Name</label>
                                    <div className="text-lg font-medium text-white mt-1">{profile.name}</div>
                                </div>
                                <div>
                                    <label className="text-xs text-gray-500 font-bold uppercase tracking-widest">Email Address</label>
                                    <div className="text-lg font-medium text-white mt-1">{profile.email}</div>
                                </div>
                                <div>
                                    <label className="text-xs text-gray-500 font-bold uppercase tracking-widest">Authentication Method</label>
                                    <div className="mt-2 flex items-center gap-3">
                                        {profile.auth_method === 'google' ? (
                                            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400">
                                                <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor"><path d="M12.48 10.92v3.28h7.84c-.24 1.84-.853 3.187-1.787 4.133-1.147 1.147-2.933 2.4-6.053 2.4-4.827 0-8.6-3.893-8.6-8.72s3.773-8.72 8.6-8.72c2.6 0 4.507 1.027 5.907 2.347l2.307-2.307C18.747 1.44 16.133 0 12.48 0 5.867 0 .307 5.387.307 12s5.56 12 12.173 12c3.573 0 6.267-1.173 8.373-3.36 2.16-2.16 2.84-5.213 2.84-7.667 0-.76-.053-1.467-.173-2.053H12.48z" /></svg>
                                                <span className="font-bold">Google Authentication</span>
                                            </div>
                                        ) : (
                                            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-700/50 border border-slate-600 text-slate-300">
                                                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
                                                <span className="font-bold">Email / Password</span>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Education/Switching Guidance */}
                        <div className="bg-blue-500/10 border border-blue-500/20 rounded-2xl p-6">
                            <h3 className="text-xl font-bold text-blue-400 mb-4 flex items-center gap-2">
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                Switching Authentication Methods
                            </h3>
                            <div className="space-y-4 text-blue-100/80 leading-relaxed">
                                <p>
                                    We support both Google Authentication and traditional Email/Password login. If you started with one and want to switch to the other, here is how:
                                </p>
                                <ul className="list-disc ml-6 space-y-2">
                                    <li>
                                        <strong>Linking Google:</strong> If you currently use a password but want to use Google, simply use the "Sign in with Google" button on the login page next time. If your emails match, your account should link automatically.
                                    </li>
                                    <li>
                                        <strong>Setting a Password:</strong> If you use Google but want to add a password, you can use the "Forgot Password" link on the login page to set one.
                                    </li>
                                    <li>
                                        <strong>Consistency:</strong> Using Google is generally recommended for security and ease of use.
                                    </li>
                                </ul>
                                <div className="mt-4 p-4 bg-blue-400/10 rounded-lg text-sm italic">
                                    <strong>Note:</strong> If you experience any issues linking your accounts, please contact an administrator to verify your email addresses match exactly.
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Sidebar / Quick Tips */}
                    <div className="space-y-6">
                        <div className="bg-slate-800 p-6 rounded-2xl border border-slate-700 shadow-xl">
                            <h3 className="text-lg font-bold mb-4">Account Security</h3>
                            <p className="text-sm text-gray-400 mb-4">
                                Keep your account safe by using a strong password or a trusted Google account.
                            </p>
                            <button
                                onClick={() => window.location.href = '/forgot-password'}
                                className="w-full py-2 px-4 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm font-bold transition-colors"
                            >
                                Reset Password
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Profile
