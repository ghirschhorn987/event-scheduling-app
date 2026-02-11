import { useEffect, useState } from 'react'
import { Link, useOutletContext } from 'react-router-dom'
import Header from '../components/Header'

export default function EventsListPage({ session }) {
    const [events, setEvents] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        async function fetchEvents() {
            try {
                const token = session?.access_token
                const headers = token ? { 'Authorization': `Bearer ${token}` } : {}

                const res = await fetch('/api/events', { headers })
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
    }, [])

    if (loading) return <div className="p-4">Loading events...</div>

    return (
        <>
            <Header session={session} />
            <div className="max-w-4xl mx-auto px-4 pb-4">
                <h1 className="text-2xl font-bold mb-2 text-white">Upcoming Events</h1>

                {events.length === 0 ? (
                    <p className="text-gray-400">No upcoming events scheduled.</p>
                ) : (
                    <div className="bg-slate-800 rounded-lg border border-slate-700 shadow-xl overflow-hidden">
                        <div className="flex flex-col">
                            {events.map((event, index) => {
                                const reserveCount = (event.counts?.waitlist || 0) + (event.counts?.holding || 0)
                                const dateStr = new Date(event.event_date).toLocaleString([], {
                                    weekday: 'short', month: 'short', day: 'numeric',
                                    hour: 'numeric', minute: '2-digit'
                                })

                                return (
                                    <div
                                        key={event.id}
                                        className={`p-4 flex flex-col gap-3 ${index !== events.length - 1 ? 'border-b border-slate-700' : ''}`}
                                    >
                                        {/* Row 1: Name and Date */}
                                        <div className="flex justify-between items-start gap-4">
                                            <h3 className="font-bold text-white text-lg leading-tight">
                                                {event.name}
                                            </h3>
                                            <span className="text-blue-400 font-medium text-sm whitespace-nowrap text-right">
                                                {dateStr}
                                            </span>
                                        </div>

                                        {/* Row 2: Status, Roster/Reserve, Action */}
                                        <div className="flex justify-between items-center">
                                            <div className="flex items-center gap-3 text-sm">
                                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${event.status === 'SCHEDULED' ? 'bg-green-900 text-green-300' :
                                                    event.status === 'CANCELLED' ? 'bg-red-900 text-red-300' :
                                                        'bg-yellow-900 text-yellow-300'
                                                    }`}>
                                                    {event.status}
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
