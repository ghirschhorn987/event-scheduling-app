import { Link, useNavigate, useLocation } from 'react-router-dom'
import { supabase } from '../supabaseClient'
import { useEffect, useState } from 'react'

export default function Header({ session }) {
    const navigate = useNavigate()
    const location = useLocation()
    const [userName, setUserName] = useState('')

    useEffect(() => {
        if (session?.user) {
            fetchUserProfile(session.user)
        }
    }, [session])

    const fetchUserProfile = async (user) => {
        try {
            // Check for mock user first to avoid unnecessary DB calls if using mock
            if (user.email === "mock.user.1@test.com" || user.user_metadata?.name) {
                // Use metadata if available or mock defaults, but real app uses profiles
                // Let's prefer fetching from profiles for consistency
            }

            const { data, error } = await supabase
                .from('profiles')
                .select('name')
                .eq('id', user.id)
                .single()

            if (data?.name) {
                setUserName(data.name)
            } else {
                // Fallback to metadata or email
                setUserName(user.user_metadata?.name || user.email)
            }
        } catch (e) {
            console.error("Header profile check failed", e)
            setUserName(user.email)
        }
    }

    const handleSignOut = async () => {
        await supabase.auth.signOut()
    }

    return (
        <header className="bg-slate-800 shadow mb-2">
            <div className="w-full px-8 py-3 flex justify-between items-center">
                <div className="flex items-center">
                    {location.pathname === '/events' ? (
                        <span className="text-xl font-bold text-gray-400 cursor-default select-none">
                            Events
                        </span>
                    ) : (
                        <Link to="/events" className="text-xl font-bold text-white hover:text-blue-400">
                            Events
                        </Link>
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
