import { useEffect, useState } from 'react'
import { supabase } from '../supabaseClient'

export default function Dashboard({ session }) {
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

                // 2. Get Next Event
                const now = new Date().toISOString()
                console.log("Fetching events >", now)
                const { data: events, error: eventError } = await supabase
                    .from('events')
                    .select('*')
                    .eq('status', 'SCHEDULED')
                    .gt('event_date', now)
                    .order('event_date', { ascending: true })
                    .limit(1)

                console.log("Events found:", events)
                if (eventError) console.error("Event Error:", eventError)

                const event = events?.[0]
                setNextEvent(event)

                if (event) {
                    // 3. Get Signups
                    const { data: signupData, error: signupError } = await supabase
                        .from('event_signups')
                        .select('*, profiles(name)')
                        .eq('event_id', event.id)
                        .order('created_at', { ascending: true }) // approximate ordering

                    if (signupError) throw signupError
                    setSignups(signupData || [])
                }

            } catch (error) {
                console.error("Error fetching dashboard data:", error)
            } finally {
                setLoading(false)
            }
        }
        fetchData()
    }, [session, refreshTrigger])

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

    // Membership check (assuming any group membership counts for now, or match logic)
    // Spec: "If a user is in the USER_GROUP associated with the Event"
    // PROVISIONAL: We assume the user is a member if they have a non-null user_group_id.
    const isMember = userProfile?.user_group_id != null

    const safeDate = (d) => {
        if (!d) return 'TBD'
        const date = new Date(d)
        return isNaN(date.getTime()) ? 'Invalid Date' : date.toLocaleString()
    }

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
                },
                body: JSON.stringify({
                    event_id: nextEvent.id,
                    user_id: session.user.id
                })
            })

            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.detail || "Failed to join")
            }

            refresh()
        } catch (error) {
            console.error(error)
            alert(error.message)
        }
    }

    const handleDelete = async () => {
        const { error } = await supabase.from('event_signups').delete().eq('event_id', nextEvent.id).eq('user_id', session.user.id)
        if (error) alert(error.message)
        refresh()
    }

    // -- RENDER --

    if (loading) return <div className="loading-screen">Loading...</div>

    if (!nextEvent) return (
        <div className="dashboard">
            <header><h2>Dashboard</h2><button className="secondary-btn" onClick={() => supabase.auth.signOut()}>Sign Out</button></header>
            <div className="event-info">
                <h3>No Upcoming Events</h3>
                <p>There are no events scheduled at this time.</p>
            </div>
        </div>
    )

    console.log("Rendering Dashboard with Event:", nextEvent)
    const eventDate = safeDate(nextEvent.event_date)

    // 1. Check Cancellation
    if (isCanceled) {
        return (
            <div className="dashboard">
                <header><h2>Dashboard</h2><button className="secondary-btn" onClick={() => supabase.auth.signOut()}>Sign Out</button></header>
                <div className="alert alert-warning">This event has been CANCELLED.</div>
            </div>
        )
    }

    // 2. Not Open message
    if (!isRosterOpen) {
        return (
            <div className="dashboard">
                <header><h2>Dashboard</h2><button className="secondary-btn" onClick={() => supabase.auth.signOut()}>Sign Out</button></header>
                <div className="event-info">
                    <h3>Next Event: {nextEvent.name}</h3>
                    <p className="date">{eventDate}</p>
                    <div className="alert">
                        Roster signup opens at {safeDate(nextEvent.roster_sign_up_open)}. <br />
                        Waitlist signup opens at {safeDate(nextEvent.waitlist_sign_up_open)}.
                    </div>
                </div>
            </div>
        )
    }

    // 3. Lists View
    return (
        <div className="dashboard">
            <header>
                <h2>Dashboard</h2>
                <div>
                    <span style={{ marginRight: '1rem', color: '#94a3b8' }}>{userProfile?.email} ({isMember ? "Member" : "Guest"})</span>
                    <button className="secondary-btn" onClick={() => supabase.auth.signOut()}>Sign Out</button>
                </div>
            </header>

            <div className="event-info">
                <h3>{nextEvent.name}</h3>
                <p className="event-date">Happening on: {eventDate}</p>

                {!isMember && now < reserveOpenTime && (
                    <div className="alert alert-warning">Reserve list sign up is not yet open.</div>
                )}

                <div className="actions" style={{ marginTop: '1rem' }}>
                    {userSignup ? (
                        <button className="danger-btn" onClick={handleDelete}>Remove My Name</button>
                    ) : (
                        <button
                            className="primary-btn"
                            onClick={handleJoin}
                            disabled={!isMember && now < reserveOpenTime}
                        >
                            Add My Name
                        </button>
                    )}
                </div>
            </div>

            <div className="lists-container">
                <ListColumn title="Event Roster" items={eventList} max={nextEvent.max_signups} />
                <ListColumn title="Wait List" items={waitList} />
                <ListColumn title="Holding Area" items={holdingList} isHolding />
            </div>
        </div>
    )
}

function ListColumn({ title, items, max, isHolding }) {
    return (
        <div className="list-column">
            <h4>{title} {max ? `(${items.length}/${max})` : `(${items.length})`}</h4>
            <ul className="list-items">
                {items.length === 0 && <li style={{ padding: '0.5rem', color: '#64748b' }}>Empty</li>}
                {items.map((item, idx) => (
                    <li key={item.id} className="list-item">
                        <div>
                            <span className="sequence">
                                {isHolding && !item.sequence_number ? '-' : (item.sequence_number || idx + 1)}
                            </span>
                            {item.profiles?.name || item.profiles?.email || 'Unknown'}
                        </div>
                    </li>
                ))}
            </ul>
        </div>
    )
}
