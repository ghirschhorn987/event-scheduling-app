import { useState, useEffect } from 'react'
import { Link, useParams } from 'react-router-dom'
import { supabase } from '../supabaseClient'
import Header from '../components/Header'

const AdminGroupDetail = ({ session }) => {
    const { groupId } = useParams()
    const [group, setGroup] = useState(null)
    const [members, setMembers] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [allProfiles, setAllProfiles] = useState([])
    const [searchQuery, setSearchQuery] = useState("")
    const [selectedProfileIds, setSelectedProfileIds] = useState([])
    const [isDropdownOpen, setIsDropdownOpen] = useState(false)
    const [processing, setProcessing] = useState(false)
    const [isEditingMetadata, setIsEditingMetadata] = useState(false)
    const [editForm, setEditForm] = useState({
        name: "",
        description: "",
        google_group_id: "",
        group_email: "",
        guest_limit: 0
    })

    useEffect(() => {
        fetchData()
        fetchAllProfiles()
    }, [groupId])

    useEffect(() => {
        if (group) {
            setEditForm({
                name: group.name || "",
                description: group.description || "",
                google_group_id: group.google_group_id || "",
                group_email: group.group_email || "",
                guest_limit: group.guest_limit || 0
            })
        }
    }, [group])

    const fetchAllProfiles = async () => {
        try {
            const sessionData = await supabase.auth.getSession()
            const token = sessionData.data.session?.access_token
            const res = await fetch('/api/admin/profiles', {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            const json = await res.json()
            setAllProfiles(json.data)
        } catch (err) {
            console.error("Error fetching profiles:", err)
        }
    }

    const fetchData = async () => {
        setLoading(true)
        try {
            const sessionData = await supabase.auth.getSession()
            const token = sessionData.data.session?.access_token
            const headers = { 'Authorization': `Bearer ${token}` }

            // Fetch group info
            const groupsRes = await fetch('/api/admin/user_groups', { headers })
            const groupsJson = await groupsRes.json()
            const groupInfo = groupsJson.data.find(g => g.id === groupId)
            setGroup(groupInfo)

            // Fetch members
            const res = await fetch(`/api/admin/groups/${groupId}/members`, { headers })
            if (!res.ok) throw new Error("Failed to fetch group members")
            const json = await res.json()
            setMembers(json.data)
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    const handleSaveMetadata = async () => {
        setProcessing(true)
        try {
            const sessionData = await supabase.auth.getSession()
            const token = sessionData.data.session?.access_token

            const res = await fetch(`/api/admin/groups/${groupId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(editForm)
            })

            const json = await res.json()
            if (!res.ok) throw new Error(json.detail || "Failed to update group metadata")

            setIsEditingMetadata(false)
            await fetchData()
        } catch (err) {
            alert(err.message)
        } finally {
            setProcessing(false)
        }
    }

    const addMembersBatch = async () => {
        if (selectedProfileIds.length === 0) return
        setProcessing(true)
        try {
            const sessionData = await supabase.auth.getSession()
            const token = sessionData.data.session?.access_token

            const res = await fetch(`/api/admin/groups/${groupId}/members/batch`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ profile_ids: selectedProfileIds })
            })

            const json = await res.json()
            if (!res.ok) throw new Error(json.detail || "Failed to add members")

            setSelectedProfileIds([])
            setSearchQuery("")
            setIsDropdownOpen(false)
            await fetchData() // Refresh members
        } catch (err) {
            alert(err.message)
        } finally {
            setProcessing(false)
        }
    }

    const removeMember = async (profileId, name) => {
        if (!window.confirm(`Are you sure you want to remove ${name} from this group?`)) return
        setProcessing(true)
        try {
            const sessionData = await supabase.auth.getSession()
            const token = sessionData.data.session?.access_token

            const res = await fetch(`/api/admin/groups/${groupId}/members/${profileId}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            })

            if (!res.ok) throw new Error("Failed to remove member")

            await fetchData() // Refresh
        } catch (err) {
            alert(err.message)
        } finally {
            setProcessing(false)
        }
    }

    // Filter profiles: not already in group AND matches search
    const availableProfiles = allProfiles.filter(p =>
        !members.some(m => m.id === p.id) &&
        (p.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
            p.email?.toLowerCase().includes(searchQuery.toLowerCase()))
    )

    const toggleProfileSelection = (id) => {
        setSelectedProfileIds(prev =>
            prev.includes(id) ? prev.filter(pId => pId !== id) : [...prev, id]
        )
    }

    if (loading) return <div className="loading-screen">Loading Group Details...</div>
    if (!group) return <div className="p-8 text-center text-white">Group not found</div>

    return (
        <div className="dashboard-container">
            <Header session={session} />

            <div className="admin-header-container mb-6 flex justify-between items-start">
                <div>
                    <Link to="/admin/groups" className="text-blue-400 hover:text-blue-300 text-sm flex items-center gap-1 mb-2">
                        <span>&larr;</span> Back to Groups List
                    </Link>
                    <h1 className="text-3xl font-bold flex items-center gap-3">
                        {group.name}
                        <span className="text-lg font-normal text-gray-500">Member List</span>
                    </h1>
                    <p className="text-gray-400 mt-1 max-w-2xl">{group.description}</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                {/* Member List Table */}
                <div className="lg:col-span-2">
                    <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden shadow-xl">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-slate-900/50 text-gray-300 text-sm uppercase tracking-wider">
                                    <th className="p-4 border-b border-slate-700">Player</th>
                                    <th className="p-4 border-b border-slate-700">Email</th>
                                    <th className="p-4 border-b border-slate-700 text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-700/50">
                                {members.length === 0 ? (
                                    <tr>
                                        <td colSpan="3" className="p-8 text-center text-gray-500 italic">
                                            No members found in this group.
                                        </td>
                                    </tr>
                                ) : (
                                    members.map(member => (
                                        <tr key={member.id} className="hover:bg-slate-700/30 transition-colors">
                                            <td className="p-4">
                                                <div className="font-semibold text-white">{member.name}</div>
                                            </td>
                                            <td className="p-4">
                                                <div className="text-gray-400 text-sm">{member.email}</div>
                                            </td>
                                            <td className="p-4 text-right">
                                                <button
                                                    onClick={() => removeMember(member.id, member.name)}
                                                    className="text-red-400 hover:text-red-300 transition-colors p-2 rounded-lg hover:bg-red-500/10"
                                                    title="Remove from Group"
                                                    disabled={processing}
                                                >
                                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                                    </svg>
                                                </button>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Sidebar */}
                <div className="lg:col-span-1">
                    <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-xl sticky top-24">

                        <div className="mb-6 pb-6 border-b border-slate-700/50">
                            <div className="flex justify-between items-center mb-4">
                                <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Group Metadata</h4>
                                {!isEditingMetadata && (
                                    <button
                                        onClick={() => setIsEditingMetadata(true)}
                                        className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1"
                                    >
                                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                                        </svg>
                                        Edit
                                    </button>
                                )}
                            </div>

                            {isEditingMetadata ? (
                                <div className="space-y-4">
                                    <div>
                                        <label className="block text-xs text-gray-400 mb-1">Group Name</label>
                                        <input
                                            type="text"
                                            value={editForm.name}
                                            onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                                            className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white text-sm focus:ring-1 focus:ring-blue-500 outline-none"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-xs text-gray-400 mb-1">Description</label>
                                        <textarea
                                            value={editForm.description}
                                            onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                                            className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white text-sm focus:ring-1 focus:ring-blue-500 outline-none h-20 resize-none"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-xs text-gray-400 mb-1">Google Group ID</label>
                                        <input
                                            type="text"
                                            value={editForm.google_group_id}
                                            onChange={(e) => setEditForm({ ...editForm, google_group_id: e.target.value })}
                                            placeholder="e.g. users@skeddle.club"
                                            className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white text-sm focus:ring-1 focus:ring-blue-500 outline-none"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-xs text-gray-400 mb-1">Group Email</label>
                                        <input
                                            type="email"
                                            value={editForm.group_email}
                                            onChange={(e) => setEditForm({ ...editForm, group_email: e.target.value })}
                                            placeholder="e.g. notify@skeddle.club"
                                            className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white text-sm focus:ring-1 focus:ring-blue-500 outline-none"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-xs text-gray-400 mb-1">Guest Limit</label>
                                        <input
                                            type="number"
                                            min="0"
                                            value={editForm.guest_limit}
                                            onChange={(e) => setEditForm({ ...editForm, guest_limit: parseInt(e.target.value) || 0 })}
                                            className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white text-sm focus:ring-1 focus:ring-blue-500 outline-none"
                                        />
                                    </div>

                                    <div className="flex gap-2 pt-2">
                                        <button
                                            onClick={handleSaveMetadata}
                                            disabled={processing}
                                            className="flex-1 bg-green-600 hover:bg-green-500 text-white text-xs font-bold py-2 rounded transition-colors disabled:opacity-50"
                                        >
                                            {processing ? 'Saving...' : 'Save Changes'}
                                        </button>
                                        <button
                                            onClick={() => {
                                                setIsEditingMetadata(false)
                                                // Reset form
                                                if (group) {
                                                    setEditForm({
                                                        name: group.name || "",
                                                        description: group.description || "",
                                                        google_group_id: group.google_group_id || "",
                                                        group_email: group.group_email || ""
                                                    })
                                                }
                                            }}
                                            disabled={processing}
                                            className="flex-1 bg-slate-700 hover:bg-slate-600 text-white text-xs font-bold py-2 rounded transition-colors disabled:opacity-50"
                                        >
                                            Cancel
                                        </button>
                                    </div>
                                </div>
                            ) : (
                                <div className="space-y-4">
                                    <div>
                                        <div className="text-xs text-gray-500">Google Group ID</div>
                                        <div className="text-white font-mono text-sm">{group.google_group_id || <span className="text-gray-600 italic">Not Set</span>}</div>
                                    </div>
                                    <div>
                                        <div className="text-xs text-gray-500">Group Email</div>
                                        <div className="text-white font-mono text-sm">
                                            {group.group_email ? (
                                                <a href={`mailto:${group.group_email}`} className="text-blue-400 hover:text-blue-300 hover:underline">{group.group_email}</a>
                                            ) : (
                                                <span className="text-gray-600 italic">Not Set</span>
                                            )}
                                        </div>
                                    </div>
                                    <div>
                                        <div className="text-xs text-gray-500">Internal ID</div>
                                        <div className="text-white font-mono text-xs truncate" title={group.id}>{group.id}</div>
                                    </div>
                                    <div>
                                        <div className="text-xs text-gray-500">Guest Limit</div>
                                        <div className="text-white font-mono text-xs">{group.guest_limit || 0}</div>
                                    </div>
                                </div>
                            )}
                        </div>

                        <h3 className="text-xl font-bold text-white mb-2">Add Members</h3>
                        <p className="text-gray-400 text-sm mb-6">Select users to add to <strong>{group.name}</strong>.</p>

                        <div className="space-y-4 relative">
                            <div className="relative">
                                <span className="absolute left-3 top-3.5 text-gray-500">
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                    </svg>
                                </span>
                                <input
                                    type="text"
                                    value={searchQuery}
                                    onChange={(e) => {
                                        setSearchQuery(e.target.value)
                                        setIsDropdownOpen(true)
                                    }}
                                    onFocus={() => setIsDropdownOpen(true)}
                                    placeholder="Search by name or email..."
                                    className="w-full bg-slate-900 border border-slate-700 rounded-lg py-3 pl-10 pr-3 text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all text-sm"
                                />

                                {isDropdownOpen && (
                                    <div className="absolute z-50 w-full mt-2 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl max-h-64 overflow-y-auto overflow-x-hidden">
                                        {availableProfiles.length === 0 ? (
                                            <div className="p-4 text-center text-gray-500 text-sm">No new users found</div>
                                        ) : (
                                            availableProfiles.map(p => (
                                                <div
                                                    key={p.id}
                                                    onClick={() => toggleProfileSelection(p.id)}
                                                    className="p-3 border-b border-slate-800 last:border-0 hover:bg-slate-800 cursor-pointer flex items-center justify-between transition-colors group"
                                                >
                                                    <div className="min-w-0 flex-1">
                                                        <div className="text-sm font-semibold text-white truncate">{p.name}</div>
                                                        <div className="text-xs text-gray-500 truncate">{p.email}</div>
                                                    </div>
                                                    <div className={`w-5 h-5 rounded border ${selectedProfileIds.includes(p.id) ? 'bg-blue-500 border-blue-500 ml-2' : 'border-slate-600 ml-2 group-hover:border-slate-400'} flex items-center justify-center transition-all`}>
                                                        {selectedProfileIds.includes(p.id) && (
                                                            <svg className="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" />
                                                            </svg>
                                                        )}
                                                    </div>
                                                </div>
                                            ))
                                        )}
                                    </div>
                                )}
                            </div>

                            {selectedProfileIds.length > 0 && (
                                <div className="pt-2">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">{selectedProfileIds.length} Selected</span>
                                        <button
                                            onClick={() => setSelectedProfileIds([])}
                                            className="text-xs text-blue-400 hover:text-blue-300"
                                        >
                                            Clear All
                                        </button>
                                    </div>
                                    <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto p-1">
                                        {selectedProfileIds.map(id => {
                                            const p = allProfiles.find(ap => ap.id === id)
                                            return (
                                                <span key={id} className="bg-blue-500/10 text-blue-400 text-xs px-2 py-1 rounded-full border border-blue-500/20 flex items-center gap-1">
                                                    {p?.name || 'User'}
                                                    <button onClick={() => toggleProfileSelection(id)} className="hover:text-blue-200">
                                                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                                                        </svg>
                                                    </button>
                                                </span>
                                            )
                                        })}
                                    </div>
                                </div>
                            )}

                            <button
                                onClick={addMembersBatch}
                                disabled={processing || selectedProfileIds.length === 0}
                                className="w-full bg-blue-500 hover:bg-blue-400 text-white font-bold py-3 rounded-lg transition-all shadow-lg active:scale-95 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed mt-4"
                            >
                                {processing ? (
                                    <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                                ) : (
                                    <>
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                                        </svg>
                                        Add {selectedProfileIds.length > 0 ? `${selectedProfileIds.length} ` : ''}to Group
                                    </>
                                )}
                            </button>
                        </div>

                        {/* Dropdown background overlay to close when clicking outside */}
                        {isDropdownOpen && (
                            <div
                                className="fixed inset-0 z-40 outline-none focus:outline-none"
                                onClick={() => setIsDropdownOpen(false)}
                            ></div>
                        )}
                    </div>
                </div>

            </div>
        </div>
    )
}

export default AdminGroupDetail
