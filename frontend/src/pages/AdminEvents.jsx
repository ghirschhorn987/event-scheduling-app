import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { supabase } from '../supabaseClient'
import Header from '../components/Header'

const EVENT_STATUSES = [
    "NOT_YET_OPEN",
    "OPEN_FOR_ROSTER",
    "OPEN_FOR_RESERVES",
    "PRELIMINARY_ORDERING",
    "FINAL_ORDERING",
    "FINISHED",
    "CANCELLED"
]

const AdminEvents = ({ session }) => {
    const [events, setEvents] = useState([])
    const [cancelledDates, setCancelledDates] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [activeTab, setActiveTab] = useState('events') // 'events' or 'blocklist'

    // Blocklist Form
    const [blockDate, setBlockDate] = useState('')
    const [blockReason, setBlockReason] = useState('')

    useEffect(() => {
        fetchData()
    }, [])

    const fetchData = async () => {
        setLoading(true)
        setError(null)
        try {
            const sessionData = await supabase.auth.getSession()
            const token = sessionData.data.session?.access_token

            const [eventsRes, datesRes] = await Promise.all([
                fetch('/api/admin/events', { headers: { 'Authorization': `Bearer ${token}` } }),
                fetch('/api/admin/cancelled_dates', { headers: { 'Authorization': `Bearer ${token}` } })
            ])

            if (!eventsRes.ok) throw new Error("Failed to fetch events")
            if (!datesRes.ok) throw new Error("Failed to fetch cancelled dates")

            const eventsJson = await eventsRes.json()
            const datesJson = await datesRes.json()

            setEvents(eventsJson.data)
            setCancelledDates(datesJson.data)

        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    const handleStatusUpdate = async (eventId, newStatus) => {
        if (!window.confirm(`Are you sure you want to change status to ${newStatus}? This will set the mode to MANUAL.`)) return

        try {
            const sessionData = await supabase.auth.getSession()
            const token = sessionData.data.session?.access_token

            const res = await fetch(`/api/admin/events/${eventId}/status`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    status: newStatus,
                    status_determinant: "MANUAL"
                })
            })

            if (!res.ok) throw new Error("Failed to update status")

            // Refresh data
            fetchData()
        } catch (err) {
            alert(`Error: ${err.message}`)
        }
    }

    const handleAddBlockDate = async (e) => {
        e.preventDefault()
        if (!blockDate) return

        try {
            const sessionData = await supabase.auth.getSession()
            const token = sessionData.data.session?.access_token

            const res = await fetch('/api/admin/cancelled_dates', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    date: blockDate,
                    reason: blockReason
                })
            })

            if (!res.ok) throw new Error("Failed to add date")

            setBlockDate('')
            setBlockReason('')
            fetchData()
        } catch (err) {
            alert(`Error: ${err.message}`)
        }
    }

    const handleRemoveBlockDate = async (dateStr) => {
        if (!window.confirm(`Unblock ${dateStr}?`)) return

        try {
            const sessionData = await supabase.auth.getSession()
            const token = sessionData.data.session?.access_token

            const res = await fetch(`/api/admin/cancelled_dates/${dateStr}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            })

            if (!res.ok) throw new Error("Failed to remove date")

            fetchData()
        } catch (err) {
            alert(`Error: ${err.message}`)
        }
    }

    if (loading) return <div className="p-8 text-white">Loading...</div>

    return (
        <div className="min-h-screen bg-slate-900 border-t border-slate-800">
            <Header session={session} />

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <Link to="/admin" className="text-blue-400 hover:text-blue-300 mb-2 inline-block">&larr; Back to Admin</Link>
                        <h1 className="text-3xl font-bold text-white">Event Management</h1>
                    </div>
                </div>

                {error && (
                    <div className="bg-red-500/10 border border-red-500 text-red-500 px-4 py-3 rounded mb-6">
                        {error}
                    </div>
                )}

                {/* Tabs */}
                <div className="flex border-b border-slate-700 mb-6">
                    <button
                        className={`px-6 py-3 font-medium ${activeTab === 'events' ? 'text-blue-400 border-b-2 border-blue-400' : 'text-gray-400 hover:text-white'}`}
                        onClick={() => setActiveTab('events')}
                    >
                        Events List
                    </button>
                    <button
                        className={`px-6 py-3 font-medium ${activeTab === 'blocklist' ? 'text-blue-400 border-b-2 border-blue-400' : 'text-gray-400 hover:text-white'}`}
                        onClick={() => setActiveTab('blocklist')}
                    >
                        Cancelled Dates (Blocklist)
                    </button>
                </div>

                {activeTab === 'events' && (
                    <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
                        <div className="overflow-x-auto">
                            <table className="w-full text-left text-sm text-gray-400">
                                <thead className="bg-slate-700/50 text-gray-200 uppercase font-medium">
                                    <tr>
                                        <th className="px-6 py-4">Date</th>
                                        <th className="px-6 py-4">Event Type</th>
                                        <th className="px-6 py-4">Status</th>
                                        <th className="px-6 py-4">Mode</th>
                                        <th className="px-6 py-4">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-700">
                                    {events.map((event) => (
                                        <tr key={event.id} className="hover:bg-slate-700/30 transition-colors">
                                            <td className="px-6 py-4 font-medium text-white">
                                                {new Date(event.event_date).toLocaleString()}
                                            </td>
                                            <td className="px-6 py-4">{event.event_type_name}</td>
                                            <td className="px-6 py-4">
                                                <span className={`px-2 py-1 rounded text-xs font-bold ${event.status === 'CANCELLED' ? 'bg-red-500/20 text-red-400' :
                                                        event.status === 'FINISHED' ? 'bg-gray-500/20 text-gray-400' :
                                                            'bg-emerald-500/20 text-emerald-400'
                                                    }`}>
                                                    {event.status}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className={`px-2 py-1 rounded text-xs font-bold ${event.status_determinant === 'MANUAL' ? 'bg-amber-500/20 text-amber-400' : 'bg-blue-500/20 text-blue-400'
                                                    }`}>
                                                    {event.status_determinant}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <select
                                                    className="bg-slate-900 border border-slate-600 rounded px-2 py-1 text-white text-xs"
                                                    value={event.status}
                                                    onChange={(e) => handleStatusUpdate(event.id, e.target.value)}
                                                >
                                                    {EVENT_STATUSES.map(s => (
                                                        <option key={s} value={s}>{s}</option>
                                                    ))}
                                                </select>
                                            </td>
                                        </tr>
                                    ))}
                                    {events.length === 0 && (
                                        <tr>
                                            <td colSpan="5" className="px-6 py-8 text-center text-gray-500">
                                                No events found.
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {activeTab === 'blocklist' && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        <div className="md:col-span-1">
                            <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 sticky top-8">
                                <h3 className="text-xl font-bold text-white mb-4">Add Cancelled Date</h3>
                                <p className="text-gray-400 text-sm mb-6">
                                    Dates added here will prevent the auto-scheduler from creating events on these days (implementation pending).
                                </p>
                                <form onSubmit={handleAddBlockDate} className="space-y-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-300 mb-1">Date</label>
                                        <input
                                            type="date"
                                            value={blockDate}
                                            onChange={(e) => setBlockDate(e.target.value)}
                                            className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white"
                                            required
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-300 mb-1">Reason (Optional)</label>
                                        <input
                                            type="text"
                                            value={blockReason}
                                            onChange={(e) => setBlockReason(e.target.value)}
                                            placeholder="e.g. Holiday"
                                            className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white"
                                        />
                                    </div>
                                    <button
                                        type="submit"
                                        className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-2 px-4 rounded transition-colors"
                                    >
                                        Block Date
                                    </button>
                                </form>
                            </div>
                        </div>

                        <div className="md:col-span-2">
                            <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
                                <table className="w-full text-left text-sm text-gray-400">
                                    <thead className="bg-slate-700/50 text-gray-200 uppercase font-medium">
                                        <tr>
                                            <th className="px-6 py-4">Date</th>
                                            <th className="px-6 py-4">Reason</th>
                                            <th className="px-6 py-4 text-right">Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-700">
                                        {cancelledDates.map((cd) => (
                                            <tr key={cd.date} className="hover:bg-slate-700/30 transition-colors">
                                                <td className="px-6 py-4 font-medium text-white">
                                                    {new Date(cd.date).toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                                                </td>
                                                <td className="px-6 py-4">{cd.reason || '-'}</td>
                                                <td className="px-6 py-4 text-right">
                                                    <button
                                                        onClick={() => handleRemoveBlockDate(cd.date)}
                                                        className="text-red-400 hover:text-red-300 text-sm font-medium"
                                                    >
                                                        Remove
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                        {cancelledDates.length === 0 && (
                                            <tr>
                                                <td colSpan="3" className="px-6 py-8 text-center text-gray-500">
                                                    No blocklisted dates found.
                                                </td>
                                            </tr>
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}

export default AdminEvents
