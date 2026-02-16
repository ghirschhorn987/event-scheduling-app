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
                // We select profile_groups -> user_groups to check membership
                const { data: profile } = await supabase
                    .from('profiles')
                    .select('*, profile_groups(user_groups(id, name))')
                    .eq('auth_user_id', session.user.id)
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

                    // Map Group IDs
                    event.roster_user_group = event.event_types.roster_user_group
                    event.reserve_first_priority_user_group = event.event_types.reserve_first_priority_user_group
                    event.reserve_second_priority_user_group = event.event_types.reserve_second_priority_user_group

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

    // 1. Determine User Tier for this Event
    let tier = null
    const userGroupIds = userProfile?.profile_groups?.map(g => g.user_groups?.id) || []

    if (nextEvent) {
        if (nextEvent.roster_user_group && userGroupIds.includes(nextEvent.roster_user_group)) {
            tier = 1
        } else if (nextEvent.reserve_first_priority_user_group && userGroupIds.includes(nextEvent.reserve_first_priority_user_group)) {
            tier = 2
        } else if (nextEvent.reserve_second_priority_user_group && userGroupIds.includes(nextEvent.reserve_second_priority_user_group)) {
            tier = 3
        }
    }

    // 2. Determine Timings & Windows
    const rosterOpenTime = nextEvent ? new Date(nextEvent.roster_sign_up_open) : null
    const reserveOpenTime = nextEvent ? new Date(nextEvent.reserve_sign_up_open) : null
    const finalReserveTime = nextEvent ? new Date(nextEvent.final_reserve_scheduling) : null

    // Lists
    const eventList = signups.filter(s => s.list_type === 'EVENT')
    const waitList = signups.filter(s => s.list_type === 'WAITLIST')
    const holdingList = signups.filter(s => s.list_type === 'WAITLIST_HOLDING')

    // Helper to check if user is in a list
    const userSignup = signups.find(s => s.user_id === userProfile?.id)

    // 3. Determine Eligibility & Action State
    let canJoin = false
    let actionLabel = "Sign Up"
    let actionDisabled = false
    let disabledReason = null
    let targetList = "EVENT" // default

    if (nextEvent && !userSignup) {
        if (!tier) {
            actionDisabled = true
            disabledReason = "Not eligible for this event"
        } else {
            // Tier 1
            if (tier === 1) {
                if (now >= rosterOpenTime) {
                    canJoin = true
                } else {
                    actionDisabled = true
                    disabledReason = `Opens ${safeDate(rosterOpenTime)}`
                }
            }
            // Tier 2 & 3
            else {
                if (now < reserveOpenTime) {
                    actionDisabled = true
                    disabledReason = `Opens ${safeDate(reserveOpenTime)}`
                } else if (now < finalReserveTime) {
                    // Holding Period
                    canJoin = true
                    actionLabel = "Join Holding List"
                    targetList = "WAITLIST_HOLDING"
                } else {
                    // Open Access
                    canJoin = true
                }
            }
        }
    } else if (userSignup) {
        // Already signed up, can't join again
        canJoin = false
    }

    const isCanceled = nextEvent?.status === 'CANCELLED'
    if (isCanceled) {
        canJoin = false
        actionDisabled = true
        disabledReason = "Event Cancelled"
    }

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
                        <header className="mb-4 flex flex-col md:flex-row md:items-baseline md:justify-between border-b pb-2 border-slate-700">
                            <div className="flex flex-col md:flex-row md:items-baseline md:gap-4">
                                <h2 className="text-2xl font-bold">{nextEvent.name}</h2>
                                <p className="text-gray-400 text-sm md:text-base">{safeDate(nextEvent.event_date)}</p>
                            </div>
                            {/* Sign Out button removed as it is in the main Header */}
                        </header>

                        {isCanceled && (
                            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4">
                                This event has been CANCELLED.
                            </div>
                        )}

                        {/* Combined Status & Actions Compact Card */}
                        <div className="bg-slate-800 p-4 rounded shadow mb-6 border border-slate-700 flex flex-col md:flex-row items-center justify-between gap-4">

                            {/* Status Badge */}
                            <span className={`px-3 py-1 rounded text-xs font-bold uppercase tracking-wider ${nextEvent.status === 'OPEN_FOR_ROSTER' ? 'bg-green-900 text-green-300' :
                                nextEvent.status === 'OPEN_FOR_RESERVES' ? 'bg-blue-900 text-blue-300' :
                                    nextEvent.status === 'PRELIMINARY_ORDERING' ? 'bg-yellow-900 text-yellow-300' :
                                        nextEvent.status === 'FINAL_ORDERING' ? 'bg-orange-900 text-orange-300' :
                                            nextEvent.status === 'CANCELLED' ? 'bg-red-900 text-red-300' :
                                                'bg-gray-700 text-gray-300'
                                }`}>
                                {nextEvent.status.replace(/_/g, ' ')}
                            </span>

                            {/* Counts */}
                            <div className="flex gap-4 text-sm font-medium">
                                <div className="bg-slate-700 px-3 py-1 rounded">Roster: <span className="text-white">{eventList.length}</span></div>
                                <div className="bg-slate-700 px-3 py-1 rounded">Waitlist: <span className="text-white">{waitList.length}</span></div>
                                <div className="bg-slate-700 px-3 py-1 rounded">Holding: <span className="text-white">{holdingList.length}</span></div>
                            </div>

                            {/* User Status & Action */}
                            <div className="flex items-center gap-4">
                                {userSignup ? (
                                    <>
                                        <div className="text-sm text-gray-300">
                                            You are: <strong className="text-white">{userSignup.list_type.replace('_', ' ')}</strong>
                                            {userSignup.sequence_number > 0 && <span className="ml-1">#{userSignup.sequence_number}</span>}
                                        </div>
                                        <button onClick={handleDelete} className="bg-red-500/20 text-red-400 border border-red-500/50 px-3 py-1.5 rounded text-sm hover:bg-red-500 hover:text-white transition-colors">
                                            Leave
                                        </button>
                                    </>
                                ) : (
                                    <>
                                        {actionDisabled ? (
                                            <div className="flex items-center gap-2">
                                                {disabledReason && <span className="text-xs text-gray-400">{disabledReason}</span>}
                                                <button disabled className="bg-slate-700 text-gray-500 px-4 py-1.5 rounded text-sm cursor-not-allowed">
                                                    {actionLabel}
                                                </button>
                                            </div>
                                        ) : (
                                            <button onClick={handleJoin} className="primary-btn py-1.5 px-6 text-sm">
                                                {actionLabel}
                                            </button>
                                        )}
                                    </>
                                )}
                            </div>
                        </div>


                        {/* Lists Display */}
                        <div className="space-y-4">
                            <div className="bg-slate-800 p-4 rounded shadow">
                                <h3 className="font-bold border-b pb-2 mb-2">Signed Up</h3>
                                <ul>
                                    {eventList
                                        .sort((a, b) => (a.sequence_number || 9999) - (b.sequence_number || 9999))
                                        .map((s, i) => (
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
                                    {waitList
                                        .sort((a, b) => (a.sequence_number || 9999) - (b.sequence_number || 9999))
                                        .map((s, i) => (
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
                                        {/* 
                                            Logic:
                                            - If OPEN_FOR_RESERVES: Sort by Time, Show '-'
                                            - Else: Sort by Sequence (Randomized), Show Number
                                        */}
                                        {holdingList
                                            .sort((a, b) => {
                                                if (nextEvent.status === 'OPEN_FOR_RESERVES') {
                                                    return new Date(a.created_at) - new Date(b.created_at)
                                                } else {
                                                    return (a.sequence_number || 9999) - (b.sequence_number || 9999)
                                                }
                                            })
                                            .map((s, i) => (
                                                <li key={s.id} className="py-1 border-b last:border-0 flex justify-between">
                                                    <span>
                                                        {nextEvent.status === 'OPEN_FOR_RESERVES' ? '-' : (i + 1) + '.'} {s.profiles?.name || 'Guest'}
                                                    </span>
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
