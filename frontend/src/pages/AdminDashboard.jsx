import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { supabase } from '../supabaseClient'
import Header from '../components/Header'

const AdminDashboard = ({ session }) => {
    const [requests, setRequests] = useState([])
    const [userGroups, setUserGroups] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [processing, setProcessing] = useState(null) // ID of request being processed

    // Modal State
    const [modalOpen, setModalOpen] = useState(false)
    const [modalType, setModalType] = useState(null) // 'DECLINE' | 'INFO'
    const [selectedRequest, setSelectedRequest] = useState(null)
    const [modalMessage, setModalMessage] = useState("")

    useEffect(() => {
        fetchData()
    }, [])

    const fetchData = async () => {
        setLoading(true)
        try {
            const session = await supabase.auth.getSession()
            const token = session.data.session?.access_token

            const headers = { 'Authorization': `Bearer ${token}` }

            // Parallel fetch
            const [reqRes, groupRes] = await Promise.all([
                fetch('/api/admin/requests', { headers }),
                fetch('/api/admin/user_groups', { headers })
            ])

            if (reqRes.status === 403) throw new Error("Access Denied: Admin privileges required.")
            if (!reqRes.ok) throw new Error("Failed to fetch requests")
            if (!groupRes.ok) throw new Error("Failed to fetch user groups")

            const reqJson = await reqRes.json()
            const groupJson = await groupRes.json()

            setRequests(reqJson.data)
            setUserGroups(groupJson.data)
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    const handleAction = async (requestId, action, role = null, message = null) => {
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
                    note: action === 'APPROVED' ? `Approved as ${role}` : 'Declined',
                    message: message // Optional message for user
                })
            })

            if (!res.ok) throw new Error("Update failed")

            // Refresh list
            await fetchData()
            closeModal()

        } catch (err) {
            alert(err.message)
        } finally {
            setProcessing(null)
        }
    }

    const openModal = (req, type) => {
        setSelectedRequest(req)
        setModalType(type)
        setModalMessage("")
        setModalOpen(true)
    }

    const closeModal = () => {
        setModalOpen(false)
        setSelectedRequest(null)
        setModalType(null)
    }

    const submitModal = () => {
        if (!selectedRequest) return
        if (modalType === 'DECLINE') {
            handleAction(selectedRequest.id, 'DECLINED_MESSAGE', null, modalMessage)
        } else if (modalType === 'INFO') {
            handleAction(selectedRequest.id, 'INFO_NEEDED', null, modalMessage)
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
            <Header session={session} />
            <div className="admin-header-container mb-6">
                <h1 className="text-3xl font-bold">Admin Dashboard</h1>
            </div>

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
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', flexWrap: 'wrap', gap: '1rem' }}>
                                    <div style={{ flex: 1, minWidth: '300px' }}>
                                        <h3>{req.full_name}</h3>
                                        <p><strong>Email:</strong> {req.email}</p>
                                        <p><strong>Affiliation:</strong> {req.affiliation}</p>
                                        {req.referral && <p><strong>Referral:</strong> {req.referral}</p>}
                                        <p><strong>Status:</strong> <span className={`status-${req.status.toLowerCase()}`}>{req.status}</span></p>
                                        <p style={{ fontSize: '0.8rem', color: '#666' }}>Requested: {new Date(req.created_at).toLocaleString()}</p>
                                        {req.admin_notes && <p style={{ fontSize: '0.9rem', color: '#555', marginTop: '5px' }}><em>Note: {req.admin_notes}</em></p>}
                                    </div>

                                    {req.status === 'PENDING' && (
                                        <div className="actions" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', minWidth: '200px' }}>

                                            {/* Approve Section */}
                                            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                                                <select id={`role-${req.id}`} style={{ padding: '5px' }} defaultValue="">
                                                    <option value="" disabled>Select Group</option>
                                                    {userGroups.map(g => (
                                                        <option key={g.id} value={g.name}>{g.name}</option>
                                                    ))}
                                                </select>
                                                <button
                                                    onClick={() => {
                                                        const select = document.getElementById(`role-${req.id}`)
                                                        const role = select.value
                                                        if (!role) return alert("Please select a user group")
                                                        handleAction(req.id, 'APPROVED', role)
                                                    }}
                                                    disabled={processing === req.id}
                                                    className="primary-btn"
                                                    style={{ fontSize: '0.8rem', padding: '5px 10px' }}
                                                >
                                                    Approve
                                                </button>
                                            </div>

                                            {/* Other Actions */}
                                            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
                                                <button
                                                    onClick={() => openModal(req, 'INFO')}
                                                    disabled={processing === req.id}
                                                    className="secondary-btn"
                                                    style={{ fontSize: '0.8rem', padding: '5px 10px' }}
                                                >
                                                    Request Info
                                                </button>
                                            </div>

                                            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.2rem' }}>
                                                <button
                                                    onClick={() => handleAction(req.id, 'DECLINED_SILENT')}
                                                    disabled={processing === req.id}
                                                    style={{ backgroundColor: '#ff6b6b', color: 'white', border: 'none', padding: '5px 10px', borderRadius: '4px', cursor: 'pointer', fontSize: '0.8rem' }}
                                                >
                                                    Decline (Silent)
                                                </button>
                                                <button
                                                    onClick={() => openModal(req, 'DECLINE')}
                                                    disabled={processing === req.id}
                                                    style={{ backgroundColor: '#e03131', color: 'white', border: 'none', padding: '5px 10px', borderRadius: '4px', cursor: 'pointer', fontSize: '0.8rem' }}
                                                >
                                                    Decline (Msg)
                                                </button>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </section>

            {/* Modal */}
            {modalOpen && (
                <div style={{
                    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
                    backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000
                }}>
                    <div style={{ backgroundColor: 'white', padding: '2rem', borderRadius: '8px', width: '90%', maxWidth: '500px' }}>
                        <h3>
                            {modalType === 'DECLINE' ? 'Decline Request' : 'Request More Info'}
                        </h3>
                        <p style={{ marginBottom: '1rem' }}>
                            {modalType === 'DECLINE'
                                ? `Send a reason to ${selectedRequest?.full_name} for declining.`
                                : `Ask ${selectedRequest?.full_name} for more details.`}
                        </p>
                        <textarea
                            value={modalMessage}
                            onChange={(e) => setModalMessage(e.target.value)}
                            rows={5}
                            style={{ width: '100%', marginBottom: '1rem', padding: '10px' }}
                            placeholder="Enter your message here..."
                        />
                        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
                            <button onClick={closeModal} className="secondary-btn">Cancel</button>
                            <button onClick={submitModal} className="primary-btn">Send</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

export default AdminDashboard
