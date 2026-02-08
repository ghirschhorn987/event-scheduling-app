import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { supabase } from './supabaseClient'
import Dashboard from './pages/Dashboard'
import UpdatePassword from './pages/UpdatePassword'
import Login from './components/Auth/Login'
import Signup from './components/Auth/Signup'
import PasswordReset from './components/Auth/PasswordReset'
import MockAuthToolbar from './components/MockAuthToolbar'
import RequestAccess from './pages/RequestAccess'
import AdminDashboard from './pages/AdminDashboard'

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
            <MockAuthToolbar />
            <div className="app-container">
                <main className={!session ? "login-page" : ""}>
                    <Routes>
                        <Route path="/login" element={!session ? <Login /> : <Navigate to="/dashboard" />} />
                        <Route path="/signup" element={!session ? <Signup /> : <Navigate to="/dashboard" />} />
                        <Route path="/request-access" element={!session ? <RequestAccess /> : <Navigate to="/dashboard" />} />
                        <Route path="/forgot-password" element={!session ? <PasswordReset /> : <Navigate to="/dashboard" />} />
                        <Route path="/dashboard" element={session ? <Dashboard session={session} /> : <Navigate to="/login" />} />
                        <Route path="/admin" element={session ? <AdminDashboard session={session} /> : <Navigate to="/login" />} />
                        <Route path="/update-password" element={<UpdatePassword />} />
                        <Route path="/" element={<Navigate to={session ? "/dashboard" : "/login"} />} />
                    </Routes>
                </main>
            </div>
        </Router>
    )
}

export default App
