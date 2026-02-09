import { describe, it, expect } from 'vitest'
import { safeDate, subtractMinutes } from './dateUtils'

describe('dateUtils', () => {
    describe('safeDate', () => {
        it('returns TBD for null or undefined', () => {
            expect(safeDate(null)).toBe('TBD')
            expect(safeDate(undefined)).toBe('TBD')
        })

        it('returns formatted string for valid date', () => {
            const date = new Date('2024-01-01T12:00:00Z')
            // Detailed formatting depends on locale, but we check it returns a string
            const result = safeDate(date.toISOString())
            expect(result).not.toBe('Invalid Date')
            expect(result).not.toBe('TBD')
            expect(typeof result).toBe('string')
        })

        it('returns Invalid Date for malformed string', () => {
            expect(safeDate('not-a-date')).toBe('Invalid Date')
        })
    })

    describe('subtractMinutes', () => {
        it('subtracts minutes correctly', () => {
            const base = new Date('2024-01-01T12:00:00Z')
            const result = subtractMinutes(base, 60)
            const expected = new Date('2024-01-01T11:00:00Z')
            expect(result.toISOString()).toBe(expected.toISOString())
        })
    })
})
