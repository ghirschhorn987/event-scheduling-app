import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { supabase } from '../supabaseClient'
import Header from '../components/Header'

const AdminGroups = ({ session }) => {
    const [groups, setGroups] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const navigate = useNavigate()

    useEffect(() => {
        fetchGroups()
    }, [])

    const fetchGroups = async () => {
        setLoading(true)
        try {
            const sessionData = await supabase.auth.getSession()
            const token = sessionData.data.session?.access_token

            const res = await fetch('/api/admin/user_groups', {
                headers: { 'Authorization': `Bearer ${token}` }
            })

            if (!res.ok) throw new Error("Failed to fetch user groups")

            const json = await res.json()
            setGroups(json.data)
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    if (loading) return <div className="loading-screen">Loading Groups...</div>

    return (
        <div className="dashboard-container">
            <Header session={session} />

            <div className="admin-header-container mb-6 flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold">User Groups</h1>
                    <Link to="/admin" className="text-blue-400 hover:text-blue-300 text-sm flex items-center gap-1 mt-1">
                        <span>&larr;</span> Back to Admin Hub
                    </Link>
                </div>
            </div>

            {error && (
                <div className="bg-red-900/20 border border-red-900/50 text-red-500 p-4 rounded-lg mb-6">
                    {error}
                </div>
            )}

            <div className="bg-slate-800 rounded-xl border border-slate-700 shadow-xl overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse min-w-[800px]">
                        <thead>
                            <tr className="bg-slate-900/50 text-gray-300 text-xs uppercase tracking-wider">
                                <th className="p-4 border-b border-slate-700">Group Name</th>
                                <th className="p-4 border-b border-slate-700">Description</th>
                                <th className="p-4 border-b border-slate-700 text-center">Users</th>
                                <th className="p-4 border-b border-slate-700">Google Group ID</th>
                                <th className="p-4 border-b border-slate-700 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-700/50">
                            {groups.map(group => (
                                <tr key={group.id} className="hover:bg-slate-700/30 transition-colors">
                                    <td className="p-4">
                                        <div className="font-bold text-white">{group.name}</div>
                                    </td>
                                    <td className="p-4">
                                        <div className="text-gray-400 text-sm max-w-xs md:max-w-md truncate">
                                            {group.description || <span className="italic opacity-50">None</span>}
                                        </div>
                                    </td>
                                    <td className="p-4 text-center">
                                        <span className="bg-blue-600 text-white px-2.5 py-1 rounded-full text-xs font-bold shadow-sm whitespace-nowrap">
                                            {group.user_count} Users
                                        </span>
                                    </td>
                                    <td className="p-4">
                                        <div className="font-mono text-xs text-slate-500 uppercase whitespace-nowrap">
                                            {group.google_group_id || <span className="opacity-30 italic">Not Set</span>}
                                        </div>
                                    </td>
                                    <td className="p-4 text-right">
                                        <button
                                            onClick={() => navigate(`/admin/groups/${group.id}`)}
                                            className="inline-flex items-center bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-bold transition-all shadow-md active:scale-95 whitespace-nowrap"
                                        >
                                            Edit Details
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    )
}

export default AdminGroups
