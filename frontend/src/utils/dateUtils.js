export const safeDate = (d) => {
    if (!d) return 'TBD'
    const date = new Date(d)
    return isNaN(date.getTime()) ? 'Invalid Date' : date.toLocaleString()
}

export const subtractMinutes = (date, min) => new Date(date.getTime() - min * 60000)
