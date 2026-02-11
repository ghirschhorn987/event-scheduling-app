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
        <div className="error-container p-8 text-center bg-slate-800 rounded-lg shadow max-w-lg mx-auto mt-10 border border-red-900/50">
            <h2 className="text-red-500 text-2xl font-bold mb-4">Error</h2>
            <p className="text-white mb-6">{error}</p>
            <Link to="/dashboard" className="primary-btn inline-block">Back to Dashboard</Link>
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
                    <p className="text-gray-400">No pending requests.</p>
                ) : (
                    <div className="space-y-4">
                        {requests.map(req => (
                            <div key={req.id} className="bg-slate-800 p-4 rounded shadow border border-slate-700">
                                <div className="flex flex-wrap gap-4 justify-between items-start">
                                    <div className="flex-1 min-w-[300px]">
                                        <h3 className="text-xl font-bold text-white mb-2">{req.full_name}</h3>
                                        <p className="text-gray-300"><strong>Email:</strong> {req.email}</p>
                                        <p className="text-gray-300"><strong>Affiliation:</strong> {req.affiliation}</p>
                                        {req.referral && <p className="text-gray-300"><strong>Referral:</strong> {req.referral}</p>}
                                        <p className="text-gray-300 mb-1">
                                            <strong>Status:</strong> <span className={`status-${req.status.toLowerCase()} ml-2 px-2 py-0.5 rounded text-xs font-bold uppercase tracking-wider bg-yellow-900 text-yellow-200`}>{req.status}</span>
                                        </p>
                                        <p className="text-xs text-gray-500 mt-2">Requested: {new Date(req.created_at).toLocaleString()}</p>
                                        {req.admin_notes && <p className="text-sm text-gray-400 mt-1"><em>Note: {req.admin_notes}</em></p>}
                                    </div>

                                    {req.status === 'PENDING' && (
                                        <div className="flex flex-col gap-2 min-w-[200px]">

                                            {/* Approve Section */}
                                            <div className="flex gap-2 items-center">
                                                <select id={`role-${req.id}`} className="bg-slate-900 border border-slate-700 text-white p-2 rounded text-sm w-full">
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
                                                    className="bg-green-600 text-white px-3 py-1.5 rounded hover:bg-green-700 disabled:opacity-50 text-sm font-semibold"
                                                >
                                                    Approve
                                                </button>
                                            </div>

                                            {/* Other Actions */}
                                            <div className="flex gap-2 mt-2">
                                                <button
                                                    onClick={() => openModal(req, 'INFO')}
                                                    disabled={processing === req.id}
                                                    className="secondary-btn text-xs px-3 py-1.5"
                                                >
                                                    Request Info
                                                </button>
                                            </div>

                                            <div className="flex gap-2 mt-1">
                                                <button
                                                    onClick={() => handleAction(req.id, 'DECLINED_SILENT')}
                                                    disabled={processing === req.id}
                                                    className="bg-red-900/50 text-red-300 border border-red-800 hover:bg-red-900 px-3 py-1.5 rounded text-xs"
                                                >
                                                    Decline (Silent)
                                                </button>
                                                <button
                                                    onClick={() => openModal(req, 'DECLINE')}
                                                    disabled={processing === req.id}
                                                    className="bg-red-600 text-white hover:bg-red-700 px-3 py-1.5 rounded text-xs"
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
                <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
                    <div className="bg-slate-800 p-8 rounded-lg w-[90%] max-w-[500px] border border-slate-700">
                        <h3 className="text-xl font-bold mb-4 text-white">
                            {modalType === 'DECLINE' ? 'Decline Request' : 'Request More Info'}
                        </h3>
                        <p className="mb-4 text-gray-300">
                            {modalType === 'DECLINE'
                                ? `Send a reason to ${selectedRequest?.full_name} for declining.`
                                : `Ask ${selectedRequest?.full_name} for more details.`}
                        </p>
                        <textarea
                            value={modalMessage}
                            onChange={(e) => setModalMessage(e.target.value)}
                            rows={5}
                            className="w-full mb-4 p-3 bg-slate-900 border border-slate-700 rounded text-white focus:border-blue-500 outline-none"
                            placeholder="Enter your message here..."
                        />
                        <div className="flex justify-end gap-4">
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
