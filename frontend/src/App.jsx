import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { supabase } from './supabaseClient'
import { checkUserAccess } from './utils/AccessControl'
import Dashboard from './pages/Dashboard'
import UpdatePassword from './pages/UpdatePassword'
import Login from './components/Auth/Login'
import Signup from './components/Auth/Signup'
import PasswordReset from './components/Auth/PasswordReset'
import MockAuthToolbar from './components/MockAuthToolbar'
import RequestAccess from './pages/RequestAccess'
import AdminHub from './pages/AdminHub'
import AdminApprovals from './pages/AdminApprovals'
import AdminGroups from './pages/AdminGroups'
import AdminGroupDetail from './pages/AdminGroupDetail'
import AdminUsers from './pages/AdminUsers'
import AdminUserDetail from './pages/AdminUserDetail'
import EventsListPage from './pages/EventsListPage'

function App() {
    const [session, setSession] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const validateSession = async (session) => {
            if (!session?.user) {
                setSession(null)
                setLoading(false)
                return
            }

            // Check if user has a profile
            const hasAccess = await checkUserAccess(session.user.id)

            if (hasAccess) {
                setSession(session)
            } else {
                console.warn("User has no profile. Access Denied.")
                await supabase.auth.signOut()
                setSession(null)
                // We need to redirect to login with error, but we are inside useEffect.
                // Since we are setting session to null, the routing below will render <Login /> or <Navigate to="/login" />.
                // However, we want to pass the error param.
                // The cleanest way is to use window.location or navigate if context allowed, but here we can just ensure
                // the redirect happens.
                // Since <Login> is rendered when !session, we can't easily pass props via Route logic without changing it.
                // BUT: The user handles the "Redirect" manually via window.location.href or just accepts that they land on Login.
                // A better approach: Modify the URL directly to include the error parameter so Login.jsx sees it.
                const url = new URL(window.location.href)
                url.pathname = '/login'
                url.searchParams.set('error', 'access_denied')
                window.history.replaceState({}, '', url)
            }
            setLoading(false)
        }

        supabase.auth.getSession().then(({ data: { session } }) => {
            validateSession(session)
        })

        const {
            data: { subscription },
        } = supabase.auth.onAuthStateChange((_event, session) => {
            // Note: onAuthStateChange fires on initial load too in some versions/configs, 
            // but usually getSession handles the initial state.
            // We should apply the same validation here.
            // CAUTION: validation is async. 'session' might be set immediately by standard libs.
            // We should delay setting state until validation passes.

            // If it's a SIGN_OUT event, just set null
            if (_event === 'SIGNED_OUT') {
                setSession(null)
                setLoading(false)
            } else if (session) {
                // If it's a SIGN_IN or TOKEN_REFRESH, validate.
                // However, doing async work here might cause a flash of content if we aren't careful.
                // But since we are reusing the same validateSession logic...
                validateSession(session)
            }
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
                        <Route path="/event/:id" element={session ? <Dashboard session={session} /> : <Navigate to="/login" />} />
                        <Route path="/events" element={session ? <EventsListPage session={session} /> : <Navigate to="/login" />} />
                        <Route path="/admin" element={session ? <AdminHub session={session} /> : <Navigate to="/login" />} />
                        <Route path="/admin/approvals" element={session ? <AdminApprovals session={session} /> : <Navigate to="/login" />} />
                        <Route path="/admin/groups" element={session ? <AdminGroups session={session} /> : <Navigate to="/login" />} />
                        <Route path="/admin/groups/:groupId" element={session ? <AdminGroupDetail session={session} /> : <Navigate to="/login" />} />
                        <Route path="/admin/users" element={session ? <AdminUsers session={session} /> : <Navigate to="/login" />} />
                        <Route path="/admin/users/:profileId" element={session ? <AdminUserDetail session={session} /> : <Navigate to="/login" />} />
                        <Route path="/update-password" element={<UpdatePassword />} />
                        <Route path="/" element={<Navigate to={session ? "/dashboard" : "/login"} />} />
                    </Routes>
                </main>
            </div>
        </Router>
    )
}

export default App
