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
        <header className="bg-slate-800 shadow mb-6">
            <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
                <div className="flex items-center gap-6">
                    <Link to="/events" className="text-xl font-bold text-white hover:text-blue-400 whitespace-nowrap">
                        Event Scheduler
                    </Link>

                    <nav className="hidden md:flex gap-4 text-sm font-medium items-center">
                        <Link
                            to="/events"
                            className={`whitespace-nowrap hover:text-blue-400 ${location.pathname === '/events' ? 'text-blue-400' : 'text-gray-300'}`}
                        >
                            Events
                        </Link>
                        {session && (
                            <Link
                                to="/dashboard"
                                className={`whitespace-nowrap hover:text-blue-400 ${location.pathname === '/dashboard' ? 'text-blue-400' : 'text-gray-300'}`}
                            >
                                Dashboard
                            </Link>
                        )}
                        {isAdmin && (
                            <Link
                                to="/admin"
                                className={`whitespace-nowrap text-purple-400 hover:text-purple-300 ${location.pathname === '/admin' ? 'font-bold' : ''}`}
                            >
                                Admin Dashboard
                            </Link>
                        )}
                    </nav>
                </div>

                <div className="flex items-center gap-4">
                    {session ? (
                        <div className="flex items-center gap-4">
                            <span className="text-sm text-gray-300 hidden sm:inline whitespace-nowrap">
                                {session.user.email}
                            </span>
                            <button
                                onClick={handleSignOut}
                                className="text-sm text-red-500 hover:text-red-400 font-medium whitespace-nowrap"
                            >
                                Sign Out
                            </button>
                        </div>
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
