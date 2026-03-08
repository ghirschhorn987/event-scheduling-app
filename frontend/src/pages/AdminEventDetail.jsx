import { useState, useEffect } from 'react'
import { Link, useParams } from 'react-router-dom'
import { supabase } from '../supabaseClient'
import Header from '../components/Header'

const AdminEventDetail = ({ session }) => {
    const { eventId } = useParams()
    const [event, setEvent] = useState(null)
    const [users, setUsers] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    // Add user Modal state
    const [isAddModalOpen, setIsAddModalOpen] = useState(false)
    const [addType, setAddType] = useState('existing') // 'existing' or 'guest'
    const [selectedProfileId, setSelectedProfileId] = useState('')
    const [guestName, setGuestName] = useState('')
    const [targetList, setTargetList] = useState('EVENT') // 'EVENT', 'WAITLIST', 'WAITLIST_HOLDING'
    const [allProfiles, setAllProfiles] = useState([])

    useEffect(() => {
        fetchEventAndUsers()
        fetchAllProfiles()
    }, [eventId])

    const fetchAllProfiles = async () => {
        try {
            const sessionData = await supabase.auth.getSession()
            const token = sessionData.data.session?.access_token
            const res = await fetch('/api/admin/profiles', {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (res.ok) {
                const data = await res.json()
                setAllProfiles(data.data || [])
            }
        } catch (err) {
            console.error("Failed to load profiles", err)
        }
    }

    const fetchEventAndUsers = async () => {
        setLoading(true)
        setError(null)
        try {
            const sessionData = await supabase.auth.getSession()
            const token = sessionData.data.session?.access_token

            // Fetch generic events list just to find the details of this one (or we could have a specific endpoint, 
            // but we can just use the supabase client for event metadata here since admin has access)
            const { data: eventData, error: eventError } = await supabase
                .from('events')
                .select('*, event_types(name)')
                .eq('id', eventId)
                .single()

            if (eventError) throw eventError
            setEvent(eventData)

            const res = await fetch(`/api/admin/events/${eventId}/users`, {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (!res.ok) throw new Error("Failed to fetch users")
            const data = await res.json()
            setUsers(data.data || [])

        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    const handleAddUser = async (e) => {
        e.preventDefault()
        try {
            const sessionData = await supabase.auth.getSession()
            const token = sessionData.data.session?.access_token

            const payload = {
                target_list: targetList,
                is_guest: addType === 'guest'
            }
            if (addType === 'existing') {
                if (!selectedProfileId) return alert("Select a user")
                payload.profile_id = selectedProfileId
            } else {
                if (!guestName) return alert("Enter guest name")
                payload.guest_name = guestName
            }

            const res = await fetch(`/api/admin/events/${eventId}/users`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            })
            if (!res.ok) throw new Error("Failed to add user")

            setIsAddModalOpen(false)
            setAddType('existing')
            setSelectedProfileId('')
            setGuestName('')
            fetchEventAndUsers()
        } catch (err) {
            alert(`Error: ${err.message}`)
        }
    }

    const handleRemoveUser = async (signupId) => {
        if (!window.confirm("Remove this user?")) return
        try {
            const sessionData = await supabase.auth.getSession()
            const token = sessionData.data.session?.access_token

            const res = await fetch(`/api/admin/events/${eventId}/users/${signupId}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (!res.ok) throw new Error("Failed to remove user")
            fetchEventAndUsers()
        } catch (err) {
            alert(`Error: ${err.message}`)
        }
    }

    const handleMoveUser = async (signupId, newList) => {
        try {
            const sessionData = await supabase.auth.getSession()
            const token = sessionData.data.session?.access_token

            const res = await fetch(`/api/admin/events/${eventId}/users/${signupId}/move`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ target_list: newList })
            })
            if (!res.ok) throw new Error("Failed to move user")
            fetchEventAndUsers()
        } catch (err) {
            alert(`Error: ${err.message}`)
        }
    }

    const handleMoveUp = async (listType, currentIndex) => {
        if (currentIndex === 0) return

        const listUsers = users.filter(u => u.list_type === listType).sort((a, b) => a.sequence_number - b.sequence_number)
        const currentUser = listUsers[currentIndex]
        const aboveUser = listUsers[currentIndex - 1]

        // Swap sequence numbers
        moveUsersLocallyAndCommit(listType, currentUser, aboveUser)
    }

    const handleMoveDown = async (listType, currentIndex) => {
        const listUsers = users.filter(u => u.list_type === listType).sort((a, b) => a.sequence_number - b.sequence_number)
        if (currentIndex === listUsers.length - 1) return

        const currentUser = listUsers[currentIndex]
        const belowUser = listUsers[currentIndex + 1]

        // Swap sequence numbers
        moveUsersLocallyAndCommit(listType, currentUser, belowUser)
    }

    const moveUsersLocallyAndCommit = async (listType, userA, userB) => {
        // Optimistic UI Update base arrays
        const oldSeqA = userA.sequence_number
        const oldSeqB = userB.sequence_number

        const updatedUsers = users.map(u => {
            if (u.id === userA.id) return { ...u, sequence_number: oldSeqB }
            if (u.id === userB.id) return { ...u, sequence_number: oldSeqA }
            return u
        })
        setUsers(updatedUsers)

        try {
            const sessionData = await supabase.auth.getSession()
            const token = sessionData.data.session?.access_token

            const payload = {
                list_type: listType,
                items: [
                    { signup_id: userA.id, sequence_number: oldSeqB },
                    { signup_id: userB.id, sequence_number: oldSeqA }
                ]
            }

            const res = await fetch(`/api/admin/events/${eventId}/users/reorder`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            })
            if (!res.ok) throw new Error("Failed to reorder")
        } catch (err) {
            alert(`Error: ${err.message}`)
            fetchEventAndUsers() // Revert on failure
        }
    }

    const renderUserTable = (listType, title) => {
        const listUsers = users.filter(u => u.list_type === listType).sort((a, b) => a.sequence_number - b.sequence_number)

        return (
            <div className="mb-8">
                <h2 className="text-xl font-bold text-white mb-4">{title} ({listUsers.length})</h2>
                <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
                    <table className="w-full text-left text-sm text-gray-400">
                        <thead className="bg-slate-700/50 text-gray-200 uppercase font-medium">
                            <tr>
                                <th className="px-6 py-4 w-16">Seq</th>
                                <th className="px-6 py-4">Name</th>
                                <th className="px-6 py-4">Status</th>
                                <th className="px-6 py-4">Order</th>
                                <th className="px-6 py-4 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-700">
                            {listUsers.map((u, idx) => (
                                <tr key={u.id} className="hover:bg-slate-700/30 transition-colors">
                                    <td className="px-6 py-4 font-medium">{u.sequence_number}</td>
                                    <td className="px-6 py-4">
                                        {u.is_guest ? (
                                            <span className="text-yellow-400">Guest: {u.guest_name}</span>
                                        ) : (
                                            <span className="text-white">{u.profiles?.name || 'Unknown User'}</span>
                                        )}
                                        {!u.is_guest && u.profiles?.email && (
                                            <div className="text-xs text-gray-500">{u.profiles.email}</div>
                                        )}
                                    </td>
                                    <td className="px-6 py-4">
                                        <select
                                            value={u.list_type}
                                            onChange={(e) => handleMoveUser(u.id, e.target.value)}
                                            className="bg-slate-900 border border-slate-600 rounded px-2 py-1 text-white text-xs"
                                        >
                                            <option value="EVENT">Signed Up</option>
                                            <option value="WAITLIST">Waitlist</option>
                                            <option value="WAITLIST_HOLDING">Holding Area</option>
                                        </select>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex gap-1">
                                            <button
                                                onClick={() => handleMoveUp(listType, idx)}
                                                disabled={idx === 0}
                                                className="p-1 text-gray-400 hover:text-white disabled:opacity-30"
                                            >
                                                ↑
                                            </button>
                                            <button
                                                onClick={() => handleMoveDown(listType, idx)}
                                                disabled={idx === listUsers.length - 1}
                                                className="p-1 text-gray-400 hover:text-white disabled:opacity-30"
                                            >
                                                ↓
                                            </button>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <button
                                            onClick={() => handleRemoveUser(u.id)}
                                            className="text-red-400 hover:text-red-300 font-medium"
                                        >
                                            Remove
                                        </button>
                                    </td>
                                </tr>
                            ))}
                            {listUsers.length === 0 && (
                                <tr>
                                    <td colSpan="5" className="px-6 py-8 text-center text-gray-500">
                                        No users in this list.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        )
    }

    if (loading) return <div className="p-8 text-white">Loading...</div>

    return (
        <div className="min-h-screen bg-slate-900 border-t border-slate-800">
            <Header session={session} />
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <Link to="/admin/events" className="text-blue-400 hover:text-blue-300 mb-2 inline-block">&larr; Back to Events</Link>
                        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                            Manage Event Users
                        </h1>
                        {event && (
                            <p className="text-gray-400 mt-2">
                                {event.event_types?.name} - {new Date(event.event_date).toLocaleString()}
                            </p>
                        )}
                    </div>
                    <button
                        onClick={() => setIsAddModalOpen(true)}
                        className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-2 px-4 rounded transition-colors"
                    >
                        + Add User
                    </button>
                </div>

                {error && (
                    <div className="bg-red-500/10 border border-red-500 text-red-500 px-4 py-3 rounded mb-6">
                        {error}
                    </div>
                )}

                {renderUserTable("EVENT", "Signed Up")}
                {renderUserTable("WAITLIST", "Waitlist")}
                {renderUserTable("WAITLIST_HOLDING", "Holding Area")}

            </div>

            {/* Add User Modal */}
            {isAddModalOpen && (
                <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
                    <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 max-w-md w-full relative">
                        <h2 className="text-xl font-bold text-white mb-6">Add User to Event</h2>
                        <form onSubmit={handleAddUser} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">Target List</label>
                                <select
                                    className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white"
                                    value={targetList}
                                    onChange={(e) => setTargetList(e.target.value)}
                                >
                                    <option value="EVENT">Signed Up</option>
                                    <option value="WAITLIST">Waitlist</option>
                                    <option value="WAITLIST_HOLDING">Holding Area</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">User Type</label>
                                <div className="flex gap-4">
                                    <label className="flex items-center text-gray-300">
                                        <input
                                            type="radio"
                                            name="addType"
                                            value="existing"
                                            checked={addType === 'existing'}
                                            onChange={() => setAddType('existing')}
                                            className="mr-2"
                                        /> Existing User
                                    </label>
                                    <label className="flex items-center text-gray-300">
                                        <input
                                            type="radio"
                                            name="addType"
                                            value="guest"
                                            checked={addType === 'guest'}
                                            onChange={() => setAddType('guest')}
                                            className="mr-2"
                                        /> Guest
                                    </label>
                                </div>
                            </div>

                            {addType === 'existing' ? (
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">Select User</label>
                                    <select
                                        className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white"
                                        value={selectedProfileId}
                                        onChange={(e) => setSelectedProfileId(e.target.value)}
                                        required
                                    >
                                        <option value="">-- Select a User --</option>
                                        {allProfiles.map(p => (
                                            <option key={p.id} value={p.id}>{p.name} ({p.email})</option>
                                        ))}
                                    </select>
                                </div>
                            ) : (
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">Guest Name</label>
                                    <input
                                        type="text"
                                        className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white"
                                        value={guestName}
                                        onChange={(e) => setGuestName(e.target.value)}
                                        required
                                        placeholder="Enter guest's full name"
                                    />
                                </div>
                            )}

                            <div className="flex justify-end gap-3 mt-6">
                                <button
                                    type="button"
                                    onClick={() => setIsAddModalOpen(false)}
                                    className="px-4 py-2 text-gray-400 hover:text-white"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="bg-blue-600 hover:bg-blue-500 text-white font-bold py-2 px-4 rounded"
                                >
                                    Add User
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    )
}

export default AdminEventDetail
