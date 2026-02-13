import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { supabase } from '../supabaseClient'
import Header from '../components/Header'

const DAY_NAMES = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

const AdminEventTypes = ({ session }) => {
    const [eventTypes, setEventTypes] = useState([])
    const [userGroups, setUserGroups] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [showModal, setShowModal] = useState(false)
    const [editingType, setEditingType] = useState(null)
    const [processing, setProcessing] = useState(false)

    // Form state
    const [formData, setFormData] = useState({
        name: '',
        day_of_week: 0,
        time_of_day: '18:00:00',
        time_zone: 'America/Los_Angeles',
        max_signups: 15,
        roster_sign_up_open_minutes: 4320,
        reserve_sign_up_open_minutes: 720,
        initial_reserve_scheduling_minutes: 420,
        final_reserve_scheduling_minutes: 180,
        roster_user_group: '',
        reserve_first_priority_user_group: '',
        reserve_second_priority_user_group: ''
    })

    useEffect(() => {
        fetchData()
    }, [])

    const fetchData = async () => {
        setLoading(true)
        try {
            const sessionData = await supabase.auth.getSession()
            const token = sessionData.data.session?.access_token

            // Fetch event types
            const typesRes = await fetch('/api/admin/event_types', {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (!typesRes.ok) throw new Error("Failed to fetch event types")
            const typesJson = await typesRes.json()
            setEventTypes(typesJson.data)

            // Fetch user groups
            const groupsRes = await fetch('/api/admin/user_groups', {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (!groupsRes.ok) throw new Error("Failed to fetch user groups")
            const groupsJson = await groupsRes.json()
            setUserGroups(groupsJson.data)
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    const openAddModal = () => {
        setEditingType(null)
        setFormData({
            name: '',
            day_of_week: 0,
            time_of_day: '18:00:00',
            time_zone: 'America/Los_Angeles',
            max_signups: 15,
            roster_sign_up_open_minutes: 4320,
            reserve_sign_up_open_minutes: 720,
            initial_reserve_scheduling_minutes: 420,
            final_reserve_scheduling_minutes: 180,
            roster_user_group: '',
            reserve_first_priority_user_group: '',
            reserve_second_priority_user_group: ''
        })
        setShowModal(true)
    }

    const openEditModal = (eventType) => {
        setEditingType(eventType)
        setFormData({
            name: eventType.name,
            day_of_week: eventType.day_of_week,
            time_of_day: eventType.time_of_day,
            time_zone: eventType.time_zone,
            max_signups: eventType.max_signups,
            roster_sign_up_open_minutes: eventType.roster_sign_up_open_minutes,
            reserve_sign_up_open_minutes: eventType.reserve_sign_up_open_minutes,
            initial_reserve_scheduling_minutes: eventType.initial_reserve_scheduling_minutes,
            final_reserve_scheduling_minutes: eventType.final_reserve_scheduling_minutes,
            roster_user_group: eventType.roster_user_group_id || '',
            reserve_first_priority_user_group: eventType.reserve_first_priority_user_group_id || '',
            reserve_second_priority_user_group: eventType.reserve_second_priority_user_group_id || ''
        })
        setShowModal(true)
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setProcessing(true)

        try {
            const sessionData = await supabase.auth.getSession()
            const token = sessionData.data.session?.access_token

            // Convert empty strings to null for optional UUID fields
            const payload = {
                ...formData,
                roster_user_group: formData.roster_user_group || null,
                reserve_first_priority_user_group: formData.reserve_first_priority_user_group || null,
                reserve_second_priority_user_group: formData.reserve_second_priority_user_group || null
            }

            const url = editingType
                ? `/api/admin/event_types/${editingType.id}`
                : '/api/admin/event_types'

            const method = editingType ? 'PUT' : 'POST'

            const res = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            })

            const json = await res.json()
            if (!res.ok) throw new Error(json.detail || "Failed to save event type")

            setShowModal(false)
            await fetchData()
        } catch (err) {
            alert(err.message)
        } finally {
            setProcessing(false)
        }
    }

    const handleDelete = async (eventType) => {
        if (!window.confirm(`Are you sure you want to delete "${eventType.name}"? This will also delete all associated events.`)) {
            return
        }

        setProcessing(true)
        try {
            const sessionData = await supabase.auth.getSession()
            const token = sessionData.data.session?.access_token

            const res = await fetch(`/api/admin/event_types/${eventType.id}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            })

            if (!res.ok) {
                const json = await res.json()
                throw new Error(json.detail || "Failed to delete event type")
            }

            await fetchData()
        } catch (err) {
            alert(err.message)
        } finally {
            setProcessing(false)
        }
    }

    if (loading) return <div className="loading-screen">Loading Event Types...</div>

    return (
        <div className="dashboard-container">
            <Header session={session} />

            <div className="admin-header-container mb-6 flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold">Event Types</h1>
                    <Link to="/admin" className="text-blue-400 hover:text-blue-300 text-sm flex items-center gap-1 mt-1">
                        <span>&larr;</span> Back to Admin Hub
                    </Link>
                </div>
                <button
                    onClick={openAddModal}
                    className="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-3 rounded-lg font-bold transition-all shadow-lg active:scale-95 flex items-center gap-2"
                >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    Add Event Type
                </button>
            </div>

            {error && (
                <div className="bg-red-900/20 border border-red-900/50 text-red-500 p-4 rounded-lg mb-6">
                    {error}
                </div>
            )}

            <div className="bg-slate-800 rounded-xl border border-slate-700 shadow-xl overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse min-w-[1200px]">
                        <thead>
                            <tr className="bg-slate-900/50 text-gray-300 text-xs uppercase tracking-wider">
                                <th className="p-4 border-b border-slate-700">Name</th>
                                <th className="p-4 border-b border-slate-700">Day</th>
                                <th className="p-4 border-b border-slate-700">Time</th>
                                <th className="p-4 border-b border-slate-700 text-center">Max</th>
                                <th className="p-4 border-b border-slate-700">Roster Group</th>
                                <th className="p-4 border-b border-slate-700">Reserve 1st</th>
                                <th className="p-4 border-b border-slate-700">Reserve 2nd</th>
                                <th className="p-4 border-b border-slate-700 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-700/50">
                            {eventTypes.length === 0 ? (
                                <tr>
                                    <td colSpan="8" className="p-8 text-center text-gray-500 italic">
                                        No event types found. Click "Add Event Type" to create one.
                                    </td>
                                </tr>
                            ) : (
                                eventTypes.map(type => (
                                    <tr key={type.id} className="hover:bg-slate-700/30 transition-colors">
                                        <td className="p-4">
                                            <div className="font-bold text-white">{type.name}</div>
                                        </td>
                                        <td className="p-4">
                                            <div className="text-gray-300">{DAY_NAMES[type.day_of_week]}</div>
                                        </td>
                                        <td className="p-4">
                                            <div className="text-gray-300 font-mono text-sm">{type.time_of_day}</div>
                                            <div className="text-gray-500 text-xs">{type.time_zone}</div>
                                        </td>
                                        <td className="p-4 text-center">
                                            <span className="bg-blue-600 text-white px-2.5 py-1 rounded-full text-xs font-bold">
                                                {type.max_signups}
                                            </span>
                                        </td>
                                        <td className="p-4">
                                            <div className="text-gray-400 text-sm">
                                                {type.roster_user_group_name || <span className="italic opacity-50">None</span>}
                                            </div>
                                        </td>
                                        <td className="p-4">
                                            <div className="text-gray-400 text-sm">
                                                {type.reserve_first_priority_user_group_name || <span className="italic opacity-50">None</span>}
                                            </div>
                                        </td>
                                        <td className="p-4">
                                            <div className="text-gray-400 text-sm">
                                                {type.reserve_second_priority_user_group_name || <span className="italic opacity-50">None</span>}
                                            </div>
                                        </td>
                                        <td className="p-4 text-right">
                                            <div className="flex items-center justify-end gap-2">
                                                <button
                                                    onClick={() => openEditModal(type)}
                                                    className="bg-blue-600 hover:bg-blue-500 text-white px-3 py-1.5 rounded-lg text-sm font-bold transition-all shadow-md active:scale-95"
                                                    disabled={processing}
                                                >
                                                    Edit
                                                </button>
                                                <button
                                                    onClick={() => handleDelete(type)}
                                                    className="text-red-400 hover:text-red-300 transition-colors p-2 rounded-lg hover:bg-red-500/10"
                                                    title="Delete Event Type"
                                                    disabled={processing}
                                                >
                                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                                    </svg>
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Modal */}
            {showModal && (
                <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
                    <div className="bg-slate-800 rounded-xl border border-slate-700 shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                        <div className="p-6 border-b border-slate-700">
                            <h2 className="text-2xl font-bold text-white">
                                {editingType ? 'Edit Event Type' : 'Add Event Type'}
                            </h2>
                        </div>

                        <form onSubmit={handleSubmit} className="p-6 space-y-4">
                            <div>
                                <label className="block text-sm font-semibold text-gray-300 mb-2">Name *</label>
                                <input
                                    type="text"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    required
                                    className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2 px-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-semibold text-gray-300 mb-2">Day of Week *</label>
                                    <select
                                        value={formData.day_of_week}
                                        onChange={(e) => setFormData({ ...formData, day_of_week: parseInt(e.target.value) })}
                                        required
                                        className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2 px-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                    >
                                        {DAY_NAMES.map((day, idx) => (
                                            <option key={idx} value={idx}>{day}</option>
                                        ))}
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-semibold text-gray-300 mb-2">Time of Day *</label>
                                    <input
                                        type="time"
                                        step="1"
                                        value={formData.time_of_day}
                                        onChange={(e) => setFormData({ ...formData, time_of_day: e.target.value + ':00' })}
                                        required
                                        className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2 px-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                    />
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-semibold text-gray-300 mb-2">Time Zone</label>
                                    <input
                                        type="text"
                                        value={formData.time_zone}
                                        onChange={(e) => setFormData({ ...formData, time_zone: e.target.value })}
                                        className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2 px-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-semibold text-gray-300 mb-2">Max Signups *</label>
                                    <input
                                        type="number"
                                        value={formData.max_signups}
                                        onChange={(e) => setFormData({ ...formData, max_signups: parseInt(e.target.value) })}
                                        required
                                        min="1"
                                        className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2 px-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                    />
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-semibold text-gray-300 mb-2">Roster Open (minutes)</label>
                                    <input
                                        type="number"
                                        value={formData.roster_sign_up_open_minutes}
                                        onChange={(e) => setFormData({ ...formData, roster_sign_up_open_minutes: parseInt(e.target.value) })}
                                        className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2 px-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-semibold text-gray-300 mb-2">Reserve Open (minutes)</label>
                                    <input
                                        type="number"
                                        value={formData.reserve_sign_up_open_minutes}
                                        onChange={(e) => setFormData({ ...formData, reserve_sign_up_open_minutes: parseInt(e.target.value) })}
                                        className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2 px-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                    />
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-semibold text-gray-300 mb-2">Initial Reserve Scheduling (min)</label>
                                    <input
                                        type="number"
                                        value={formData.initial_reserve_scheduling_minutes}
                                        onChange={(e) => setFormData({ ...formData, initial_reserve_scheduling_minutes: parseInt(e.target.value) })}
                                        className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2 px-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-semibold text-gray-300 mb-2">Final Reserve Scheduling (min)</label>
                                    <input
                                        type="number"
                                        value={formData.final_reserve_scheduling_minutes}
                                        onChange={(e) => setFormData({ ...formData, final_reserve_scheduling_minutes: parseInt(e.target.value) })}
                                        className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2 px-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-semibold text-gray-300 mb-2">Roster User Group</label>
                                <select
                                    value={formData.roster_user_group}
                                    onChange={(e) => setFormData({ ...formData, roster_user_group: e.target.value })}
                                    className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2 px-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                >
                                    <option value="">None</option>
                                    {userGroups.map(group => (
                                        <option key={group.id} value={group.id}>{group.name}</option>
                                    ))}
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-semibold text-gray-300 mb-2">Reserve First Priority Group</label>
                                <select
                                    value={formData.reserve_first_priority_user_group}
                                    onChange={(e) => setFormData({ ...formData, reserve_first_priority_user_group: e.target.value })}
                                    className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2 px-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                >
                                    <option value="">None</option>
                                    {userGroups.map(group => (
                                        <option key={group.id} value={group.id}>{group.name}</option>
                                    ))}
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-semibold text-gray-300 mb-2">Reserve Second Priority Group</label>
                                <select
                                    value={formData.reserve_second_priority_user_group}
                                    onChange={(e) => setFormData({ ...formData, reserve_second_priority_user_group: e.target.value })}
                                    className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2 px-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                >
                                    <option value="">None</option>
                                    {userGroups.map(group => (
                                        <option key={group.id} value={group.id}>{group.name}</option>
                                    ))}
                                </select>
                            </div>

                            <div className="flex gap-3 pt-4">
                                <button
                                    type="submit"
                                    disabled={processing}
                                    className="flex-1 bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-lg transition-all shadow-lg active:scale-95 disabled:opacity-50"
                                >
                                    {processing ? 'Saving...' : (editingType ? 'Update' : 'Create')}
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setShowModal(false)}
                                    disabled={processing}
                                    className="flex-1 bg-slate-700 hover:bg-slate-600 text-white font-bold py-3 rounded-lg transition-all"
                                >
                                    Cancel
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    )
}

export default AdminEventTypes
