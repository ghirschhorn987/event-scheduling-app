export const safeDate = (d) => {
    if (!d) return 'TBD'
    const date = new Date(d)
    return isNaN(date.getTime()) ? 'Invalid Date' : date.toLocaleString()
}

export const subtractMinutes = (date, min) => new Date(date.getTime() - min * 60000)

export const formatEventDate = (dateStr) => {
    if (!dateStr) return 'TBD'
    const date = new Date(dateStr)
    if (isNaN(date.getTime())) return 'Invalid Date'

    const day = date.toLocaleDateString([], { weekday: 'short' })
    const month = date.toLocaleDateString([], { month: 'short' })
    const dateNum = date.getDate()
    const time = date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })

    return `${day}, ${month} ${dateNum} ${time}`
}

export const formatTimeUntil = (targetDateStr) => {
    if (!targetDateStr) return null
    const target = new Date(targetDateStr)
    const now = new Date()
    const diffMs = target - now

    if (diffMs <= 0) return 'now'

    const diffMins = Math.floor(diffMs / 60000)
    const h = Math.floor(diffMins / 60)
    const m = diffMins % 60

    if (h > 24) {
        const d = Math.floor(h / 24)
        return `in ${d}d ${h % 24}h`
    }
    if (h > 0) return `in ${h}h ${m}m`
    return `in ${m}m`
}

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
