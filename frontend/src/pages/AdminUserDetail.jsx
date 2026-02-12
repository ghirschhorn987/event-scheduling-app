import { useState, useEffect } from 'react'
import { Link, useParams } from 'react-router-dom'
import { supabase } from '../supabaseClient'
import Header from '../components/Header'

const AdminUserDetail = ({ session }) => {
    const { profileId } = useParams()
    const [profile, setProfile] = useState(null)
    const [allGroups, setAllGroups] = useState([])
    const [selectedGroupIds, setSelectedGroupIds] = useState([])
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)
    const [message, setMessage] = useState(null)

    useEffect(() => {
        fetchData()
    }, [profileId])

    const fetchData = async () => {
        setLoading(true)
        try {
            const sessionData = await supabase.auth.getSession()
            const token = sessionData.data.session?.access_token
            const headers = { 'Authorization': `Bearer ${token}` }

            // Fetch groups
            const groupsRes = await fetch('/api/admin/user_groups', { headers })
            const groupsJson = await groupsRes.json()
            setAllGroups(groupsJson.data)

            // Fetch profile details
            const profileRes = await fetch(`/api/admin/profiles/${profileId}`, { headers })
            if (!profileRes.ok) throw new Error("Failed to fetch player details")
            const profileJson = await profileRes.json()

            setProfile(profileJson.data)
            setSelectedGroupIds(profileJson.data.group_ids || [])
        } catch (err) {
            console.error("Error fetching data:", err)
        } finally {
            setLoading(false)
        }
    }

    const handleCheckboxChange = (groupId) => {
        setSelectedGroupIds(prev =>
            prev.includes(groupId)
                ? prev.filter(id => id !== groupId)
                : [...prev, groupId]
        )
    }

    const handleSave = async () => {
        setSaving(true)
        setMessage(null)
        try {
            const sessionData = await supabase.auth.getSession()
            const token = sessionData.data.session?.access_token

            const res = await fetch(`/api/admin/profiles/${profileId}/groups`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ group_ids: selectedGroupIds })
            })

            const json = await res.json()
            if (!res.ok) throw new Error(json.detail || "Failed to update groups")

            setMessage({ type: 'success', text: 'Group assignments updated successfully!' })

            // Auto-clear message after 3 seconds
            setTimeout(() => setMessage(null), 3000)
        } catch (err) {
            setMessage({ type: 'error', text: err.message })
        } finally {
            setSaving(false)
        }
    }

    if (loading) return <div className="loading-screen">Loading Player Details...</div>
    if (!profile) return <div className="p-8 text-center text-white">Player not found</div>

    return (
        <div className="dashboard-container text-white">
            <Header session={session} />

            <div className="admin-header-container mb-8">
                <Link to="/admin/users" className="text-blue-400 hover:text-blue-300 text-sm flex items-center gap-1 mb-2">
                    <span>&larr;</span> Back to Players List
                </Link>
                <h1 className="text-3xl font-bold flex items-center gap-3">
                    Edit Player: {profile.name}
                </h1>
                <p className="text-gray-400 mt-1 font-mono text-sm">{profile.email}</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                {/* Main Content: Group Checklist */}
                <div className="lg:col-span-2">
                    <div className="bg-slate-800 rounded-2xl border border-slate-700 shadow-xl overflow-hidden">
                        <div className="p-6 border-b border-slate-700 bg-slate-900/50">
                            <h2 className="text-xl font-bold">Group Assignments</h2>
                            <p className="text-sm text-gray-500 mt-1">Check the groups this user should belong to.</p>
                        </div>

                        <div className="p-6 space-y-4">
                            {allGroups.map(group => (
                                <div
                                    key={group.id}
                                    onClick={() => handleCheckboxChange(group.id)}
                                    className={`p-4 rounded-xl border transition-all cursor-pointer flex items-center justify-between group ${selectedGroupIds.includes(group.id)
                                            ? 'bg-purple-500/10 border-purple-500/50 shadow-lg shadow-purple-500/5'
                                            : 'bg-slate-900/40 border-slate-700 hover:border-slate-500 shadow-none'
                                        }`}
                                >
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2">
                                            <span className={`font-bold transition-colors ${selectedGroupIds.includes(group.id) ? 'text-purple-400' : 'text-white'}`}>
                                                {group.name}
                                            </span>
                                            {group.google_group_id && (
                                                <span className="text-[10px] bg-slate-700 text-gray-400 px-1.5 py-0.5 rounded font-mono">
                                                    SYNCED
                                                </span>
                                            )}
                                        </div>
                                        <div className="text-xs text-gray-500 mt-1">{group.description || 'No description provided.'}</div>
                                    </div>

                                    <div className={`w-6 h-6 rounded-lg border-2 flex items-center justify-center transition-all ${selectedGroupIds.includes(group.id)
                                            ? 'bg-purple-500 border-purple-500'
                                            : 'border-slate-600 group-hover:border-slate-400'
                                        }`}>
                                        {selectedGroupIds.includes(group.id) && (
                                            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" />
                                            </svg>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="p-6 bg-slate-900/50 border-t border-slate-700 flex items-center justify-between gap-4">
                            <div className="text-sm text-gray-400">
                                {selectedGroupIds.length} groups selected
                            </div>
                            <div className="flex items-center gap-3">
                                {message && (
                                    <span className={`text-sm font-medium ${message.type === 'success' ? 'text-emerald-400' : 'text-red-400'}`}>
                                        {message.text}
                                    </span>
                                )}
                                <button
                                    onClick={handleSave}
                                    disabled={saving}
                                    className="bg-purple-500 hover:bg-purple-400 text-white font-bold py-3 px-8 rounded-xl shadow-lg transition-all active:scale-95 disabled:opacity-50 flex items-center gap-2"
                                >
                                    {saving ? (
                                        <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                                    ) : (
                                        'Save Changes'
                                    )}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Sidebar: User Info Ref Card */}
                <div className="lg:col-span-1">
                    <div className="bg-slate-800 p-6 rounded-2xl border border-slate-700 shadow-xl sticky top-24">
                        <h3 className="text-lg font-bold mb-4">Player Info</h3>
                        <div className="space-y-4">
                            <div>
                                <label className="text-xs text-gray-500 font-bold uppercase tracking-widest">Display Name</label>
                                <div className="text-white bg-slate-900/50 p-3 rounded-lg border border-slate-700 mt-1">{profile.name}</div>
                            </div>
                            <div>
                                <label className="text-xs text-gray-500 font-bold uppercase tracking-widest">Email Address</label>
                                <div className="text-white bg-slate-900/50 p-3 rounded-lg border border-slate-700 mt-1 truncate" title={profile.email}>{profile.email}</div>
                            </div>
                            <div>
                                <label className="text-xs text-gray-500 font-bold uppercase tracking-widest">Profile ID</label>
                                <div className="text-xs text-gray-400 bg-slate-900/50 p-3 rounded-lg border border-slate-700 mt-1 font-mono break-all">{profile.id}</div>
                            </div>
                        </div>

                        <div className="mt-8 p-4 bg-blue-500/10 border border-blue-500/20 rounded-xl">
                            <div className="flex gap-3">
                                <svg className="w-5 h-5 text-blue-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <div className="text-xs text-blue-300">
                                    Adding a user to a group might trigger automated syncs if a Google Group ID is configured for that group.
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    )
}

export default AdminUserDetail
