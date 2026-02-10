import { useEffect, useState } from 'react'
import { supabase } from '../supabaseClient'
import { Link, useParams } from 'react-router-dom'
import { safeDate, subtractMinutes } from '../utils/dateUtils'
import Header from '../components/Header'

export default function Dashboard({ session }) {
    const { id } = useParams() // Get ID from URL if present
    const [loading, setLoading] = useState(true)
    const [userProfile, setUserProfile] = useState(null)
    const [nextEvent, setNextEvent] = useState(null)
    const [signups, setSignups] = useState([])
    const [refreshTrigger, setRefreshTrigger] = useState(0)

    // Fetch data
    useEffect(() => {
        async function fetchData() {
            try {
                setLoading(true)

                // 1. Get User Profile
                // We select user_groups(name) to check membership
                const { data: profile } = await supabase
                    .from('profiles')
                    .select('*, user_groups(id, name)')
                    .eq('id', session.user.id)
                    .single()

                setUserProfile(profile)

                // 2. Get Event (Specific or Next)
                let event = null

                if (id) {
                    console.log("Fetching specific event:", id)
                    // Use backend API if possible or simplified fetch
                    // For now, we use the logic we wrote: fetch and manual enrich
                    const { data, error } = await supabase
                        .from('events')
                        .select('*, event_types(*)')
                        .eq('id', id)
                        .single()

                    if (data) event = data
                } else {
                    // Fetch next event
                    const now = new Date().toISOString()
                    const { data: events } = await supabase
                        .from('events')
                        .select('*, event_types(*)') // Join types
                        .eq('status', 'SCHEDULED')
                        .gt('event_date', now)
                        .order('event_date', { ascending: true })
                        .limit(1)

                    event = events?.[0]
                }

                // ENRICHMENT (Frontend version of backend logic)
                if (event && event.event_types) {
                    // Map type fields to top level for compatibility
                    event.name = event.event_types.name
                    event.max_signups = event.event_types.max_signups

                    // Parse Date
                    const eventDate = new Date(event.event_date) // This is potentially UTC

                    // Calc times (minutes subtraction)


                    event.roster_sign_up_open = subtractMinutes(eventDate, event.event_types.roster_sign_up_open_minutes).toISOString()
                    event.reserve_sign_up_open = subtractMinutes(eventDate, event.event_types.reserve_sign_up_open_minutes).toISOString()
                    event.initial_reserve_scheduling = subtractMinutes(eventDate, event.event_types.initial_reserve_scheduling_minutes).toISOString()
                    event.final_reserve_scheduling = subtractMinutes(eventDate, event.event_types.final_reserve_scheduling_minutes).toISOString()
                    // waitlist same as roster for now
                    event.waitlist_sign_up_open = event.roster_sign_up_open
                }

                setNextEvent(event)

                if (event) {
                    // 3. Get Signups
                    const { data: signupData, error: signupError } = await supabase
                        .from('event_signups')
                        .select('*, profiles(name)')
                        .eq('event_id', event.id)
                        .order('created_at', { ascending: true }) // approximate ordering

                    if (signupError) throw signupError

                    let finalSignups = signupData || []

                    // -- MOCK AUTH: INJECT LOCAL SIGNUP --
                    const useMock = import.meta.env.VITE_USE_MOCK_AUTH === 'true'
                    if (useMock) {
                        const mockKey = `mock-signup-${event.id}-${session.user.id}`
                        const stored = localStorage.getItem(mockKey)
                        if (stored) {
                            const mockSignup = JSON.parse(stored)
                            // Avoid duplicates if somehow it got into DB
                            if (!finalSignups.some(s => s.user_id === mockSignup.user_id)) {
                                finalSignups.push(mockSignup)
                            }
                        }
                    }

                    setSignups(finalSignups)
                }

            } catch (error) {
                console.error("Error fetching dashboard data:", error)
            } finally {
                setLoading(false)
            }
        }
        fetchData()
    }, [session, refreshTrigger, id])

    const refresh = () => setRefreshTrigger(prev => prev + 1)

    // -- LOGIC --

    const now = new Date()

    // Lists
    const eventList = signups.filter(s => s.list_type === 'EVENT')
    const waitList = signups.filter(s => s.list_type === 'WAITLIST')
    const holdingList = signups.filter(s => s.list_type === 'WAITLIST_HOLDING')

    // Helper to check if user is in a list
    const userSignup = signups.find(s => s.user_id === session.user.id)

    // Timings
    const rosterOpenTime = nextEvent ? new Date(nextEvent.roster_sign_up_open) : null
    const waitlistOpenTime = nextEvent ? new Date(nextEvent.waitlist_sign_up_open) : null
    const reserveOpenTime = nextEvent ? new Date(nextEvent.reserve_sign_up_open) : null
    const initialReserveTime = nextEvent ? new Date(nextEvent.initial_reserve_scheduling) : null
    const finalReserveTime = nextEvent ? new Date(nextEvent.final_reserve_scheduling) : null

    // Membership check
    const isMember = userProfile?.user_group_id != null



    // Render Conditions
    const isRosterOpen = rosterOpenTime && now >= rosterOpenTime
    const isCanceled = nextEvent?.status === 'CANCELLED'

    // Actions
    const handleJoin = async () => {
        if (!nextEvent) return

        try {
            const response = await fetch('/api/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${session.access_token}`
                },
                body: JSON.stringify({
                    event_id: nextEvent.id,
                    user_id: session.user.id
                })
            })

            let responseData = null
            if (response.ok) {
                responseData = await response.json()
            } else {
                const errorData = await response.json()
                throw new Error(errorData.detail || "Failed to join")
            }

            // -- MOCK AUTH: SAVE LOCAL SIGNUP --
            const useMock = import.meta.env.VITE_USE_MOCK_AUTH === 'true'
            if (useMock && responseData && responseData.data) {
                const mockKey = `mock-signup-${nextEvent.id}-${session.user.id}`
                // Use the data returned by the backend which has the correct list_type/sequence logic!
                const mockSignup = {
                    ...responseData.data,
                    profiles: { name: 'Mock Guest' }
                }
                localStorage.setItem(mockKey, JSON.stringify(mockSignup))
            }

            refresh()
        } catch (error) {
            console.error(error)
            alert(error.message)
        }
    }

    const handleDelete = async () => {
        // -- MOCK AUTH: REMOVE LOCAL SIGNUP --
        const useMock = import.meta.env.VITE_USE_MOCK_AUTH === 'true'
        if (useMock) {
            const mockKey = `mock-signup-${nextEvent.id}-${session.user.id}`
            localStorage.removeItem(mockKey)
        }

        try {
            const response = await fetch('/api/remove-signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${session.access_token}`
                },
                body: JSON.stringify({
                    event_id: nextEvent.id,
                    user_id: session.user.id
                })
            })

            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.detail || "Failed to remove")
            }

            refresh()
        } catch (error) {
            console.error(error)
            alert(error.message)
        }
    }

    if (loading) return <div className="loading-screen">Loading...</div>

    // Layout
    return (
        <>
            <Header session={session} />
            <div className="dashboard-container max-w-2xl mx-auto p-4">
                {/* Back link removed as it is in Header */}

                {!nextEvent ? (
                    <div className="no-events text-center py-10">
                        <header className="mb-4 flex justify-between items-center">
                            <h2 className="text-2xl font-bold">Dashboard</h2>
                            <button className="secondary-btn" onClick={() => supabase.auth.signOut()}>Sign Out</button>
                        </header>
                        <div className="bg-slate-800 p-6 rounded shadow">
                            <h3 className="text-xl mb-2">No Upcoming Events</h3>
                            <p className="text-gray-600">Check back later for new schedules.</p>
                        </div>
                    </div>
                ) : (
                    <>
                        <header className="mb-6 flex justify-between items-center">
                            <div>
                                <h2 className="text-3xl font-bold">{nextEvent.name}</h2>
                                <p className="text-gray-600">{safeDate(nextEvent.event_date)}</p>
                            </div>
                            <button className="secondary-btn bg-gray-200 px-4 py-2 rounded" onClick={() => supabase.auth.signOut()}>Sign Out</button>
                        </header>

                        {isCanceled && (
                            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4">
                                This event has been CANCELLED.
                            </div>
                        )}

                        {/* Status Bar */}
                        <div className="bg-slate-800 p-4 rounded shadow mb-6">
                            <h3 className="font-semibold mb-2">Event Status</h3>
                            <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>Roster: {eventList.length} / {nextEvent.max_signups}</div>
                                <div>Waitlist: {waitList.length}</div>
                                <div>Holding: {holdingList.length}</div>
                            </div>
                        </div>

                        {/* User Status / Actions */}
                        <div className="bg-slate-800 p-6 rounded shadow mb-6">
                            {userSignup ? (
                                <div className="text-center">
                                    <p className="text-lg mb-4">You are: <strong>{userSignup.list_type.replace('_', ' ')}</strong> #{userSignup.sequence_number > 0 ? userSignup.sequence_number : '-'}</p>
                                    <button onClick={handleDelete} className="bg-red-500 text-white px-6 py-2 rounded hover:bg-red-600">
                                        Leave Event
                                    </button>
                                </div>
                            ) : (
                                <div className="text-center">
                                    {!isRosterOpen && !isMember ? (
                                        <div>
                                            <p className="mb-2">Signup opens: {safeDate(rosterOpenTime)}</p>
                                            <button disabled className="bg-gray-300 text-gray-500 px-6 py-2 rounded cursor-not-allowed">
                                                Not Open Yet
                                            </button>
                                        </div>
                                    ) : (
                                        <button onClick={handleJoin} className="bg-green-600 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-green-700">
                                            Sign Up Now
                                        </button>
                                    )}
                                </div>
                            )}
                        </div>

                        {/* Lists Display */}
                        <div className="space-y-4">
                            <div className="bg-slate-800 p-4 rounded shadow">
                                <h3 className="font-bold border-b pb-2 mb-2">Main Roster</h3>
                                <ul>
                                    {eventList.map((s, i) => (
                                        <li key={s.id} className="py-1 border-b last:border-0 flex justify-between">
                                            <span>{i + 1}. {s.profiles?.name || 'Guest'}</span>
                                        </li>
                                    ))}
                                    {eventList.length === 0 && <li className="text-gray-500 italic">Empty</li>}
                                </ul>
                            </div>

                            <div className="bg-slate-800 p-4 rounded shadow">
                                <h3 className="font-bold border-b pb-2 mb-2">Waitlist</h3>
                                <ul>
                                    {waitList.map((s, i) => (
                                        <li key={s.id} className="py-1 border-b last:border-0 flex justify-between">
                                            <span>{i + 1}. {s.profiles?.name || 'Guest'}</span>
                                        </li>
                                    ))}
                                    {waitList.length === 0 && <li className="text-gray-500 italic">Empty</li>}
                                </ul>
                            </div>

                            {holdingList.length > 0 && (
                                <div className="bg-slate-800 p-4 rounded shadow">
                                    <h3 className="font-bold border-b pb-2 mb-2">Holding Area</h3>
                                    <ul>
                                        {holdingList.map((s, i) => (
                                            <li key={s.id} className="py-1 border-b last:border-0 flex justify-between">
                                                <span>- {s.profiles?.name || 'Guest'}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    </>
                )}
            </div>
        </>
    )
}
