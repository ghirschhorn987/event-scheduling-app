import { Link, useNavigate, useLocation } from 'react-router-dom'
import { supabase } from '../supabaseClient'
import { useEffect, useState } from 'react'

export default function Header({ session }) {
    const navigate = useNavigate()
    const location = useLocation()
    const [userName, setUserName] = useState('')
    const [isAdmin, setIsAdmin] = useState(false)
    const [authMethod, setAuthMethod] = useState(null)

    useEffect(() => {
        if (session?.user) {
            fetchUserProfile(session.user)
        }
    }, [session])

    const fetchUserProfile = async (user) => {
        try {
            const { data, error } = await supabase
                .from('profiles')
                .select('name, auth_method, profile_groups(user_groups(name))')
                .eq('auth_user_id', user.id)
                .single()

            if (data) {
                setUserName(data.name || user.email)
                setAuthMethod(data.auth_method)

                // Check for admin/superadmin roles
                const groups = data.profile_groups || []
                const isUserAdmin = groups.some(pg =>
                    ["Super Admin", "SuperAdmin", "Admin"].includes(pg.user_groups?.name)
                )
                setIsAdmin(isUserAdmin)
            } else {
                // Fallback to metadata
                setUserName(user.user_metadata?.name || user.email)
                setIsAdmin(false)
            }
        } catch (e) {
            console.error("Header profile check failed", e)
            setUserName(user.email)
            setIsAdmin(false)
        }
    }

    const handleSignOut = async () => {
        await supabase.auth.signOut()
    }

    return (
        <header className="bg-slate-800 shadow mb-2">
            <div className="w-full px-8 py-3 flex justify-between items-center">
                <div className="flex items-center gap-8">
                    {location.pathname === '/events' ? (
                        <span className="text-xl font-bold text-gray-400 cursor-default select-none">
                            Events
                        </span>
                    ) : (
                        <Link to="/events" className="text-xl font-bold text-white hover:text-blue-400 transition-colors">
                            Events
                        </Link>
                    )}

                    {isAdmin && (
                        location.pathname.startsWith('/admin') ? (
                            <span className="text-xl font-bold text-gray-400 cursor-default select-none">
                                Admin
                            </span>
                        ) : (
                            <Link to="/admin" className="text-xl font-bold text-white hover:text-blue-400 transition-colors">
                                Admin
                            </Link>
                        )
                    )}

                    {location.pathname === '/help' ? (
                        <span className="text-xl font-bold text-gray-400 cursor-default select-none">
                            Help
                        </span>
                    ) : (
                        <Link to="/help" className="text-xl font-bold text-white hover:text-blue-400 transition-colors">
                            Help
                        </Link>
                    )}
                </div>

                <div className="flex items-center gap-8">
                    {session ? (
                        <>
                            <div className="flex flex-col items-end mr-4">
                                <div className="flex items-center gap-2">
                                    <span className="text-sm font-bold text-gray-300 whitespace-nowrap">
                                        {userName || 'Unknown Name'}
                                    </span>
                                    {authMethod === 'google' && (
                                        <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20" title="Signed in with Google">
                                            <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor"><path d="M12.48 10.92v3.28h7.84c-.24 1.84-.853 3.187-1.787 4.133-1.147 1.147-2.933 2.4-6.053 2.4-4.827 0-8.6-3.893-8.6-8.72s3.773-8.72 8.6-8.72c2.6 0 4.507 1.027 5.907 2.347l2.307-2.307C18.747 1.44 16.133 0 12.48 0 5.867 0 .307 5.387.307 12s5.56 12 12.173 12c3.573 0 6.267-1.173 8.373-3.36 2.16-2.16 2.84-5.213 2.84-7.667 0-.76-.053-1.467-.173-2.053H12.48z" /></svg>
                                        </span>
                                    )}
                                    {authMethod === 'email' && (
                                        <div className="group relative flex items-center">
                                            <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium bg-slate-700/50 text-slate-300 border border-slate-600 cursor-help" title="Signed in with Email/Password">
                                                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
                                            </span>
                                            <div className="absolute right-0 top-full mt-2 hidden group-hover:block w-48 bg-slate-800 text-xs text-gray-300 p-2 rounded shadow-lg border border-slate-700 z-50">
                                                You are currently using an Email/Password login. If you prefer, ask an admin to help link your Google Account.
                                            </div>
                                        </div>
                                    )}
                                </div>
                                <span className="text-xs text-gray-500 whitespace-nowrap">
                                    {session.user.email}
                                </span>
                            </div>
                            <button
                                onClick={handleSignOut}
                                className="text-sm text-red-500 hover:text-red-400 font-medium whitespace-nowrap"
                            >
                                Sign Out
                            </button>
                        </>
                    ) : (
                        <Link to="/login" className="text-sm text-blue-400 hover:underline whitespace-nowrap">
                            Log In
                        </Link>
                    )}
                </div>
            </div>
        </header>
    )
}
