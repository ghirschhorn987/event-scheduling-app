import { Link } from 'react-router-dom'
import Header from '../components/Header'

const AdminHub = ({ session }) => {
    return (
        <div className="dashboard-container">
            <Header session={session} />

            <div className="admin-header-container mb-8">
                <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">
                    Admin Control Center
                </h1>
                <p className="text-gray-400 mt-2">Manage users, groups, and access requests.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

                {/* Approvals Card */}
                <Link to="/admin/approvals" className="admin-card group">
                    <div className="p-6 bg-slate-800 rounded-xl border border-slate-700 hover:border-blue-500 transition-all duration-300 shadow-lg hover:shadow-blue-500/10 h-full flex flex-col">
                        <div className="w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center mb-4 group-hover:bg-blue-500/20 transition-colors">
                            <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                        </div>
                        <h2 className="text-2xl font-bold text-white mb-2">Approve Accounts</h2>
                        <p className="text-gray-400 flex-grow">Review and approve new user registration requests and assign initial groups.</p>
                        <div className="mt-4 text-blue-400 font-semibold flex items-center gap-2 group-hover:translate-x-1 transition-transform">
                            Manage Approvals <span>&rarr;</span>
                        </div>
                    </div>
                </Link>

                {/* User Groups Card */}
                <Link to="/admin/groups" className="admin-card group">
                    <div className="p-6 bg-slate-800 rounded-xl border border-slate-700 hover:border-emerald-500 transition-all duration-300 shadow-lg hover:shadow-emerald-500/10 h-full flex flex-col">
                        <div className="w-12 h-12 bg-emerald-500/10 rounded-lg flex items-center justify-center mb-4 group-hover:bg-emerald-500/20 transition-colors">
                            <svg className="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                            </svg>
                        </div>
                        <h2 className="text-2xl font-bold text-white mb-2">User Groups</h2>
                        <p className="text-gray-400 flex-grow">View list of groups, member counts, and manage group membership.</p>
                        <div className="mt-4 text-emerald-400 font-semibold flex items-center gap-2 group-hover:translate-x-1 transition-transform">
                            Manage Groups <span>&rarr;</span>
                        </div>
                    </div>
                </Link>

                {/* User Management Card */}
                <Link to="/admin/users" className="admin-card group">
                    <div className="p-6 bg-slate-800 rounded-xl border border-slate-700 hover:border-purple-500 transition-all duration-300 shadow-lg hover:shadow-purple-500/10 h-full flex flex-col">
                        <div className="w-12 h-12 bg-purple-500/10 rounded-lg flex items-center justify-center mb-4 group-hover:bg-purple-500/20 transition-colors">
                            <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                            </svg>
                        </div>
                        <h2 className="text-2xl font-bold text-white mb-2">User Management</h2>
                        <p className="text-gray-400 flex-grow">Search and manage individual player profiles and their associated groups.</p>
                        <div className="mt-4 text-purple-400 font-semibold flex items-center gap-2 group-hover:translate-x-1 transition-transform">
                            Manage Users <span>&rarr;</span>
                        </div>
                    </div>
                </Link>

                {/* Event Types Card */}
                <Link to="/admin/event-types" className="admin-card group">
                    <div className="p-6 bg-slate-800 rounded-xl border border-slate-700 hover:border-orange-500 transition-all duration-300 shadow-lg hover:shadow-orange-500/10 h-full flex flex-col">
                        <div className="w-12 h-12 bg-orange-500/10 rounded-lg flex items-center justify-center mb-4 group-hover:bg-orange-500/20 transition-colors">
                            <svg className="w-6 h-6 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                        </div>
                        <h2 className="text-2xl font-bold text-white mb-2">Event Types</h2>
                        <p className="text-gray-400 flex-grow">Manage event type definitions, schedules, and group restrictions.</p>
                        <div className="mt-4 text-orange-400 font-semibold flex items-center gap-2 group-hover:translate-x-1 transition-transform">
                            Manage Event Types <span>&rarr;</span>
                        </div>
                    </div>
                </Link>

                {/* Analytics or Other (Placeholder) */}
                <div className="hidden lg:flex bg-slate-800/50 p-6 rounded-xl border border-slate-700/50 border-dashed flex-col items-center justify-center text-center opacity-60">
                    <p className="text-gray-500 italic text-sm">More functionality coming soon...</p>
                </div>

            </div>
        </div>
    )
}

export default AdminHub
