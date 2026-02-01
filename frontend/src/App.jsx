import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { supabase } from './supabaseClient'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import UpdatePassword from './pages/UpdatePassword'

function App() {
    const [session, setSession] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        supabase.auth.getSession().then(({ data: { session } }) => {
            setSession(session)
            setLoading(false)
        })

        const {
            data: { subscription },
        } = supabase.auth.onAuthStateChange((_event, session) => {
            setSession(session)
            setLoading(false)
        })

        return () => subscription.unsubscribe()
    }, [])

    if (loading) return <div className="loading-screen">Loading...</div>

    return (
        <Router>
            <Routes>
                <Route path="/" element={!session ? <Login /> : <Navigate to="/dashboard" />} />
                <Route path="/dashboard" element={session ? <Dashboard session={session} /> : <Navigate to="/" />} />
                <Route path="/update-password" element={<UpdatePassword />} />
            </Routes>
        </Router>
    )
}

export default App
