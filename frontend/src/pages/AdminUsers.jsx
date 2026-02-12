import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { supabase } from '../supabaseClient'
import Header from '../components/Header'

const AdminUsers = ({ session }) => {
    const [profiles, setProfiles] = useState([])
    const [loading, setLoading] = useState(true)
    const [searchQuery, setSearchQuery] = useState("")

    useEffect(() => {
        fetchProfiles()
    }, [])

    const fetchProfiles = async () => {
        setLoading(true)
        try {
            const sessionData = await supabase.auth.getSession()
            const token = sessionData.data.session?.access_token
            const res = await fetch('/api/admin/profiles', {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            const json = await res.json()
            setProfiles(json.data)
        } catch (err) {
            console.error("Error fetching profiles:", err)
        } finally {
            setLoading(false)
        }
    }

    const filteredProfiles = profiles.filter(p =>
        p.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.email?.toLowerCase().includes(searchQuery.toLowerCase())
    )

    if (loading) return <div className="loading-screen">Loading Players...</div>

    return (
        <div className="dashboard-container text-white">
            <Header session={session} />

            <div className="admin-header-container mb-8">
                <Link to="/admin" className="text-blue-400 hover:text-blue-300 text-sm flex items-center gap-1 mb-2">
                    <span>&larr;</span> Back to Admin Hub
                </Link>
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
                            User Management
                        </h1>
                        <p className="text-gray-400 mt-1">View and manage all registered player profiles.</p>
                    </div>
                </div>
            </div>

            {/* Search Bar */}
            <div className="mb-6 relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                </span>
                <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search players by name or email..."
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl py-4 pl-12 pr-4 text-white focus:ring-2 focus:ring-purple-500 outline-none transition-all shadow-lg"
                />
            </div>

            <div className="bg-slate-800 rounded-2xl border border-slate-700 overflow-hidden shadow-2xl">
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-slate-900/50 text-gray-400 text-xs uppercase tracking-widest font-bold">
                                <th className="p-5 border-b border-slate-700">Name</th>
                                <th className="p-5 border-b border-slate-700">Email</th>
                                <th className="p-5 border-b border-slate-700 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-700/50">
                            {filteredProfiles.length === 0 ? (
                                <tr>
                                    <td colSpan="3" className="p-10 text-center text-gray-500 italic">
                                        No players found matching your search.
                                    </td>
                                </tr>
                            ) : (
                                filteredProfiles.map(p => (
                                    <tr key={p.id} className="hover:bg-slate-700/30 transition-colors group">
                                        <td className="p-5">
                                            <div className="font-bold text-white group-hover:text-purple-400 transition-colors">{p.name || 'Anonymous Player'}</div>
                                        </td>
                                        <td className="p-5">
                                            <div className="text-gray-400 text-sm font-mono">{p.email}</div>
                                        </td>
                                        <td className="p-5 text-right">
                                            <Link
                                                to={`/admin/users/${p.id}`}
                                                className="inline-flex items-center gap-2 bg-slate-700 hover:bg-purple-600 text-white text-sm font-bold py-2 px-4 rounded-lg transition-all active:scale-95"
                                            >
                                                Manage Groups
                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                                                </svg>
                                            </Link>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            <div className="mt-6 text-center text-gray-500 text-sm">
                Showing {filteredProfiles.length} of {profiles.length} total users
            </div>
        </div>
    )
}

export default AdminUsers
