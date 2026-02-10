import { Link, useNavigate, useLocation } from 'react-router-dom'
import { supabase } from '../supabaseClient'
import { useEffect, useState } from 'react'

export default function Header({ session }) {
    const navigate = useNavigate()
    const location = useLocation()
    const [isAdmin, setIsAdmin] = useState(false)

    useEffect(() => {
        if (session?.user) {
            checkAdminForHeader(session.user)
        }
    }, [session])

    const checkAdminForHeader = async (user) => {
        // Simple check similar to backend logic or based on mock data
        // For efficiency, we might want to store this in session or context, but fetching here is fine for now.

        // 1. Mock Admin Check
        if (user.email === "mock.admin@test.com" || user.id === "793db7d3-7996-4669-8714-8340f784085c") {
            setIsAdmin(true)
            return
        }

        // 2. Real DB Check
        try {
            const { data, error } = await supabase
                .from('profiles')
                .select('user_groups(name)')
                .eq('id', user.id)
                .single()

            if (data?.user_groups?.name === 'Admin') {
                setIsAdmin(true)
            }
        } catch (e) {
            console.error("Header admin check failed", e)
        }
    }

    const handleSignOut = async () => {
        await supabase.auth.signOut()
        // If on a protected page, App.jsx might redirect, or we can force it
        // navigate('/login') // Let auth state change handle it
    }

    return (
        <header className="bg-white shadow mb-6">
            <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
                <div className="flex items-center gap-6">
                    <Link to="/events" className="text-xl font-bold text-gray-800 hover:text-blue-600">
                        Event Scheduler
                    </Link>

                    <nav className="hidden md:flex gap-4 text-sm font-medium">
                        <Link
                            to="/events"
                            className={`hover:text-blue-600 ${location.pathname === '/events' ? 'text-blue-600' : 'text-gray-600'}`}
                        >
                            Events
                        </Link>
                        {session && (
                            <Link
                                to="/dashboard"
                                className={`hover:text-blue-600 ${location.pathname === '/dashboard' ? 'text-blue-600' : 'text-gray-600'}`}
                            >
                                Dashboard
                            </Link>
                        )}
                        {isAdmin && (
                            <Link
                                to="/admin"
                                className={`text-purple-600 hover:text-purple-800 ${location.pathname === '/admin' ? 'font-bold' : ''}`}
                            >
                                Admin Dashboard
                            </Link>
                        )}
                    </nav>
                </div>

                <div className="flex items-center gap-4">
                    {session ? (
                        <div className="flex items-center gap-4">
                            <span className="text-sm text-gray-500 hidden sm:inline">
                                {session.user.email}
                            </span>
                            <button
                                onClick={handleSignOut}
                                className="text-sm text-red-600 hover:text-red-800 font-medium"
                            >
                                Sign Out
                            </button>
                        </div>
                    ) : (
                        <Link to="/login" className="text-sm text-blue-600 hover:underline">
                            Log In
                        </Link>
                    )}
                </div>
            </div>
        </header>
    )
}
