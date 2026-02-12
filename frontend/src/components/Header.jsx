import { Link, useNavigate, useLocation } from 'react-router-dom'
import { supabase } from '../supabaseClient'
import { useEffect, useState } from 'react'

export default function Header({ session }) {
    const navigate = useNavigate()
    const location = useLocation()
    const [userName, setUserName] = useState('')
    const [isAdmin, setIsAdmin] = useState(false)

    useEffect(() => {
        if (session?.user) {
            fetchUserProfile(session.user)
        }
    }, [session])

    const fetchUserProfile = async (user) => {
        try {
            const { data, error } = await supabase
                .from('profiles')
                .select('name, profile_groups(user_groups(name))')
                .eq('auth_user_id', user.id)
                .single()

            if (data) {
                setUserName(data.name || user.email)

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
                </div>

                <div className="flex items-center gap-8">
                    {session ? (
                        <>
                            <span className="text-sm text-gray-300 whitespace-nowrap">
                                {userName || session.user.email}
                            </span>
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
