import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Header from '../components/Header'

export default function EventsListPage({ session }) {
    const [events, setEvents] = useState([])
    const [loading, setLoading] = useState(true)
    const [timeFilter, setTimeFilter] = useState('future') // 'future', 'past', 'all'
    const [statusFilter, setStatusFilter] = useState('ALL') // 'ALL', 'OPEN_FOR_ROSTER', etc.

    useEffect(() => {
        async function fetchEvents() {
            setLoading(true)
            try {
                const token = session?.access_token
                const headers = token ? { 'Authorization': `Bearer ${token}` } : {}

                const res = await fetch(`/api/events?filter=${timeFilter}`, { headers })
                if (res.ok) {
                    const data = await res.json()
                    setEvents(data)
                } else {
                    console.error("Failed to fetch events")
                }
            } catch (e) {
                console.error("Error:", e)
            } finally {
                setLoading(false)
            }
        }
        fetchEvents()
    }, [timeFilter])

    const filteredEvents = events.filter(e => statusFilter === 'ALL' || e.status === statusFilter)

    return (
        <>
            <Header session={session} />
            <div className="max-w-4xl mx-auto px-4 pb-4 mt-6">
                <div className="flex flex-col md:flex-row md:items-center justify-between mb-4">
                    <h1 className="text-2xl font-bold text-white mb-2 md:mb-0">Events</h1>

                    <div className="flex gap-2">
                        <select
                            value={timeFilter}
                            onChange={(e) => setTimeFilter(e.target.value)}
                            className="bg-slate-800 border border-slate-700 text-white rounded px-3 py-1.5 text-sm outline-none focus:border-blue-500 transition-colors"
                        >
                            <option value="future">Future Events</option>
                            <option value="past">Past Events</option>
                            <option value="all">All Events</option>
                        </select>
                        <select
                            value={statusFilter}
                            onChange={(e) => setStatusFilter(e.target.value)}
                            className="bg-slate-800 border border-slate-700 text-white rounded px-3 py-1.5 text-sm outline-none focus:border-blue-500 transition-colors"
                        >
                            <option value="ALL">All Statuses</option>
                            <option value="OPEN_FOR_ROSTER">Open for Roster</option>
                            <option value="OPEN_FOR_RESERVES">Open for Reserves</option>
                            <option value="PRELIMINARY_ORDERING">Preliminary Ordering</option>
                            <option value="FINAL_ORDERING">Final Ordering</option>
                            <option value="CLOSED">Closed/Finished</option>
                            <option value="CANCELLED">Cancelled</option>
                        </select>
                    </div>
                </div>

                {loading ? (
                    <div className="p-4 text-gray-400">Loading events...</div>
                ) : filteredEvents.length === 0 ? (
                    <p className="text-gray-400">No events found matching criteria.</p>
                ) : (
                    <div className="bg-slate-800 rounded-lg border border-slate-700 shadow-xl overflow-hidden">
                        <div className="flex flex-col">
                            {filteredEvents.map((event, index) => {
                                const reserveCount = (event.counts?.waitlist || 0) + (event.counts?.holding || 0)
                                const dateObj = new Date(event.event_date)

                                // Formatting date for UI
                                const dayAbbr = dateObj.toLocaleDateString([], { weekday: 'short' })
                                const dateStr = dateObj.toLocaleDateString([], { month: 'short', day: 'numeric' })
                                const timeStr = dateObj.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })

                                return (
                                    <div
                                        key={event.id}
                                        className={`p-4 flex flex-col gap-3 ${index !== filteredEvents.length - 1 ? 'border-b border-slate-700' : ''}`}
                                    >
                                        <div className="flex justify-between items-start gap-4">
                                            <h3 className="font-bold text-white text-lg leading-tight">
                                                {event.name}
                                            </h3>
                                            <div className="text-right whitespace-nowrap">
                                                <div className="text-blue-400 font-bold text-base leading-tight">
                                                    {dayAbbr}, <span className="text-white">{dateStr}</span>
                                                </div>
                                                <div className="text-gray-400 text-sm">
                                                    {timeStr}
                                                </div>
                                            </div>
                                        </div>

                                        <div className="flex justify-between items-center mt-1">
                                            <div className="flex items-center gap-3 text-sm">
                                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${event.status === 'OPEN_FOR_ROSTER' ? 'bg-green-900 text-green-300' :
                                                    event.status === 'OPEN_FOR_RESERVES' ? 'bg-blue-900 text-blue-300' :
                                                        event.status === 'PRELIMINARY_ORDERING' ? 'bg-yellow-900 text-yellow-300' :
                                                            event.status === 'FINAL_ORDERING' ? 'bg-orange-900 text-orange-300' :
                                                                event.status === 'CANCELLED' ? 'bg-red-900 text-red-300' :
                                                                    'bg-gray-700 text-gray-300'
                                                    }`}>
                                                    {event.status.replace(/_/g, ' ')}
                                                </span>
                                                <span className="text-gray-400 font-mono">
                                                    {event.counts?.roster || 0} / {reserveCount}
                                                </span>
                                            </div>

                                            <Link
                                                to={`/event/${event.id}`}
                                                className="inline-block bg-blue-600 !text-white px-4 py-1.5 rounded text-sm font-bold hover:bg-blue-500 transition-colors shadow-sm"
                                            >
                                                View
                                            </Link>
                                        </div>
                                    </div>
                                )
                            })}
                        </div>
                    </div>
                )}
            </div>
        </>
    )
}

