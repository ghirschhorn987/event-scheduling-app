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
            <div className="max-w-4xl mx-auto p-4">
                <h1 className="text-2xl font-bold mb-6">Upcoming Events</h1>

                {events.length === 0 ? (
                    <p>No upcoming events scheduled.</p>
                ) : (
                    <div className="grid gap-4">
                        {events.map(event => (
                            <div key={event.id} className="border p-4 rounded shadow bg-white flex justify-between items-center">
                                <div>
                                    <h2 className="text-xl font-semibold">{event.name}</h2>
                                    <p className="text-gray-600">
                                        {new Date(event.event_date).toLocaleString([], {
                                            weekday: 'long', month: 'short', day: 'numeric',
                                            hour: 'numeric', minute: '2-digit'
                                        })}
                                    </p>
                                    <div className="text-sm mt-2 text-gray-500">
                                        Status: <span className="font-medium">{event.status}</span>
                                    </div>
                                </div>

                                <div className="flex items-center gap-6">
                                    <div className="text-right text-sm">
                                        <div title="People signed up for the main roster">
                                            Roster: <strong>{event.counts?.roster || 0}</strong>/{event.max_signups}
                                        </div>
                                        <div title="People on the waitlist">
                                            Waitlist: <strong>{event.counts?.waitlist || 0}</strong>
                                        </div>
                                        <div title="People in the holding area">
                                            Holding: <strong>{event.counts?.holding || 0}</strong>
                                        </div>
                                    </div>

                                    <Link
                                        to={`/event/${event.id}`}
                                        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                                    >
                                        View / Sign Up
                                    </Link>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </>
    )
}
