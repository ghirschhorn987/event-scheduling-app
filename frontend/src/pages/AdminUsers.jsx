import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { supabase } from '../supabaseClient'
import Header from '../components/Header'

const AdminUsers = ({ session }) => {
    const [profiles, setProfiles] = useState([])
    const [loading, setLoading] = useState(true)
    const [searchQuery, setSearchQuery] = useState("")
    const [isUploading, setIsUploading] = useState(false)
    const [uploadResult, setUploadResult] = useState(null)
    const fileInputRef = useRef(null)

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

    const handleFileUpload = async (e) => {
        const file = e.target.files[0]
        if (!file) return

        setIsUploading(true)
        setUploadResult(null)

        try {
            const text = await file.text()
            // Very simple CSV parser (assuming no commas in names/emails/groups)
            // Format expected: Name,Email,Groups (groups comma-separated or semicolon)
            // Let's assume standard: Name,Email,"Group1;Group2"
            // To be robust, let's use a simple regex for CSV line splitting
            const lines = text.split('\n').filter(l => l.trim() !== '')

            // Assuming first line is header: Name,Email,Groups
            const headers = lines[0].toLowerCase().split(',')
            const nameIdx = headers.findIndex(h => h.includes('name'))
            const emailIdx = headers.findIndex(h => h.includes('email'))
            const groupsIdx = headers.findIndex(h => h.includes('group'))

            if (nameIdx === -1 || emailIdx === -1) {
                setUploadResult({ error: "CSV must contain at least 'Name' and 'Email' columns." })
                setIsUploading(false)
                return
            }

            const payload = []
            for (let i = 1; i < lines.length; i++) {
                // Split correctly handling possible quotes
                const row = lines[i].match(/(".*?"|[^",\s]+)(?=\s*,|\s*$)/g) || lines[i].split(',')
                if (row.length < 2) continue

                const name = row[nameIdx]?.replace(/^"|"$/g, '').trim() || ''
                const email = row[emailIdx]?.replace(/^"|"$/g, '').trim() || ''
                if (!email) continue

                let groups = []
                if (groupsIdx !== -1 && row[groupsIdx]) {
                    const groupStr = row[groupsIdx].replace(/^"|"$/g, '').trim()
                    // Allow splitting by semicolon or pipe since comma is used for CSV columns
                    // If the user uses standard CSV quotes, a comma inside could be preserved.
                    // For simplicity, let's split by semicolon:
                    groups = groupStr.split(/;|\|/).map(g => g.trim()).filter(g => g)
                }

                payload.push({
                    full_name: name,
                    email: email,
                    groups: groups
                })
            }

            const sessionData = await supabase.auth.getSession()
            const token = sessionData.data.session?.access_token

            const res = await fetch('/api/admin/users/bulk-pre-approve', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            })

            const json = await res.json()
            if (res.ok) {
                setUploadResult({ success: `Imported ${json.success_count} users successfully.`, errors: json.errors })
                fetchProfiles() // Refresh the list
            } else {
                setUploadResult({ error: json.detail || "Upload failed." })
            }
        } catch (err) {
            console.error(err)
            setUploadResult({ error: "An error occurred while parsing or uploading the CSV." })
        } finally {
            setIsUploading(false)
            if (fileInputRef.current) fileInputRef.current.value = '' // Reset input
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

                    <div className="flex items-center gap-3">
                        <input
                            type="file"
                            accept=".csv"
                            className="hidden"
                            ref={fileInputRef}
                            onChange={handleFileUpload}
                        />
                        <button
                            onClick={() => fileInputRef.current?.click()}
                            disabled={isUploading}
                            className={`bg-purple-600 hover:bg-purple-500 text-white font-bold py-2 px-6 rounded-xl transition-all shadow-lg flex items-center justify-center gap-2 ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}
                        >
                            {isUploading ? (
                                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                            ) : (
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                                </svg>
                            )}
                            {isUploading ? 'Importing...' : 'Bulk Import CSV'}
                        </button>
                    </div>
                </div>
            </div>

            {/* Upload Results */}
            {uploadResult && (
                <div className={`mb-6 p-4 rounded-xl border ${uploadResult.error ? 'bg-red-900/40 border-red-700 text-red-200' : 'bg-green-900/40 border-green-700 text-green-200'}`}>
                    {uploadResult.error ? (
                        <div className="flex items-center gap-2">
                            <svg className="w-5 h-5 text-red-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                            <span className="font-bold">{uploadResult.error}</span>
                        </div>
                    ) : (
                        <div>
                            <div className="flex items-center gap-2 font-bold mb-2">
                                <svg className="w-5 h-5 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" /></svg>
                                {uploadResult.success}
                            </div>
                            {uploadResult.errors?.length > 0 && (
                                <div className="mt-2 text-sm text-yellow-300">
                                    <p className="font-bold mb-1">However, some errors occurred:</p>
                                    <ul className="list-disc pl-5 space-y-1">
                                        {uploadResult.errors.map((e, idx) => (
                                            <li key={idx}>{e}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}

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
