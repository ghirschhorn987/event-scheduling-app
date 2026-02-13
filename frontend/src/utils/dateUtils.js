export const safeDate = (d) => {
    if (!d) return 'TBD'
    const date = new Date(d)
    return isNaN(date.getTime()) ? 'Invalid Date' : date.toLocaleString()
}

export const subtractMinutes = (date, min) => new Date(date.getTime() - min * 60000)

export const determineEventStatus = (event) => {
    // If cancelled manually, respect it
    if (event.status === 'CANCELLED') return 'CANCELLED'

    const now = new Date()
    const rosterOpen = new Date(event.roster_sign_up_open)
    const reserveOpen = new Date(event.reserve_sign_up_open)
    const initialScheduling = new Date(event.initial_reserve_scheduling)
    const finalScheduling = new Date(event.final_reserve_scheduling)
    const eventStart = new Date(event.event_date)

    if (now < rosterOpen) return 'NOT_YET_OPEN'
    if (now < reserveOpen) return 'OPEN_FOR_ROSTER'
    if (now < initialScheduling) return 'OPEN_FOR_RESERVES'
    if (now < finalScheduling) return 'PRELIMINARY_ORDERING'
    if (now < eventStart) return 'FINAL_ORDERING'
    return 'FINISHED'
}
