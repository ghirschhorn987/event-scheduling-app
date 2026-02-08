import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { supabase } from '../supabaseClient'

const AdminDashboard = () => {
    const [requests, setRequests] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [processing, setProcessing] = useState(null) // ID of request being processed

    const navigate = useNavigate()

    useEffect(() => {
        fetchRequests()
    }, [])

    const fetchRequests = async () => {
        setLoading(true)
        try {
            // We use our custom API because it handles the "Admin Check" securely
            const session = await supabase.auth.getSession()
            const token = session.data.session?.access_token

            const res = await fetch('/api/admin/requests', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })

            if (res.status === 403) {
                throw new Error("Access Denied: Admin privileges required.")
            }
            if (!res.ok) {
                throw new Error("Failed to fetch requests")
            }

            const json = await res.json()
            setRequests(json.data)
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    const handleAction = async (requestId, action, role = null) => {
        setProcessing(requestId)
        try {
            const session = await supabase.auth.getSession()
            const token = session.data.session?.access_token

            const res = await fetch('/api/admin/requests/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    request_id: requestId,
                    action: action,
                    role: role,
                    note: action === 'APPROVED' ? `Approved as ${role}` : 'Declined'
                })
            })

            if (!res.ok) throw new Error("Update failed")

            // Refresh list
            await fetchRequests()

        } catch (err) {
            alert(err.message)
        } finally {
            setProcessing(null)
        }
    }

    if (loading) return <div className="loading-screen">Loading Admin Panel...</div>
    if (error) return (
        <div className="error-container" style={{ padding: '2rem', textAlign: 'center' }}>
            <h2 style={{ color: 'red' }}>Error</h2>
            <p>{error}</p>
            <Link to="/dashboard" className="primary-btn">Back to Dashboard</Link>
        </div>
    )

    return (
        <div className="dashboard-container">
            <header className="dashboard-header">
                <h1>Admin Dashboard</h1>
                <div className="header-actions">
                    <Link to="/dashboard" className="secondary-btn">Back to App</Link>
                </div>
            </header>

            <section className="admin-section">
                <h2>Pending Registration Requests</h2>

                {requests.length === 0 ? (
                    <p>No pending requests.</p>
                ) : (
                    <div className="requests-list">
                        {requests.map(req => (
                            <div key={req.id} className="request-card" style={{
                                border: '1px solid #ddd', padding: '1rem', marginBottom: '1rem',
                                borderRadius: '8px', backgroundColor: '#fff'
                            }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                                    <div>
                                        <h3>{req.full_name}</h3>
                                        <p><strong>Email:</strong> {req.email}</p>
                                        <p><strong>Affiliation:</strong> {req.affiliation}</p>
                                        {req.referral && <p><strong>Referral:</strong> {req.referral}</p>}
                                        <p><strong>Status:</strong> <span className={`status-${req.status.toLowerCase()}`}>{req.status}</span></p>
                                        <p style={{ fontSize: '0.8rem', color: '#666' }}>Requested: {new Date(req.created_at).toLocaleString()}</p>
                                    </div>

                                    {req.status === 'PENDING' && (
                                        <div className="actions" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                            <p style={{ fontSize: '0.9rem', marginBottom: '0.2rem' }}>Approve as:</p>
                                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                                <button
                                                    onClick={() => handleAction(req.id, 'APPROVED', 'Primary')}
                                                    disabled={processing === req.id}
                                                    className="primary-btn"
                                                    style={{ fontSize: '0.8rem', padding: '5px 10px' }}
                                                >
                                                    Primary
                                                </button>
                                                <button
                                                    onClick={() => handleAction(req.id, 'APPROVED', 'Secondary')}
                                                    disabled={processing === req.id}
                                                    className="secondary-btn"
                                                    style={{ fontSize: '0.8rem', padding: '5px 10px' }}
                                                >
                                                    Secondary
                                                </button>
                                                <button
                                                    onClick={() => handleAction(req.id, 'APPROVED', 'Guest')}
                                                    disabled={processing === req.id}
                                                    className="secondary-btn"
                                                    style={{ fontSize: '0.8rem', padding: '5px 10px' }}
                                                >
                                                    Guest
                                                </button>
                                            </div>
                                            <button
                                                onClick={() => handleAction(req.id, 'DECLINED')}
                                                disabled={processing === req.id}
                                                style={{ backgroundColor: '#ff6b6b', color: 'white', border: 'none', padding: '5px', borderRadius: '4px', cursor: 'pointer', marginTop: '5px' }}
                                            >
                                                Decline
                                            </button>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </section>
        </div>
    )
}

export default AdminDashboard
