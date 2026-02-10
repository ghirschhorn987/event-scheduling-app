import { describe, it, expect, vi } from 'vitest'
import { checkUserAccess } from '../utils/AccessControl'
import { supabase } from '../supabaseClient'

// Mock the supabase client
vi.mock('../supabaseClient', () => ({
    supabase: {
        from: vi.fn(() => ({
            select: vi.fn(() => ({
                eq: vi.fn(() => ({
                    maybeSingle: vi.fn()
                }))
            }))
        }))
    }
}))

describe('AccessControl Utility', () => {
    it('should return true when profile exists', async () => {
        // Setup mock chain
        const maybeSingleMock = vi.fn().mockResolvedValue({ data: { id: '123' }, error: null })

        supabase.from.mockImplementation(() => ({
            select: () => ({
                eq: () => ({
                    maybeSingle: maybeSingleMock
                })
            })
        }))

        const result = await checkUserAccess('123')
        expect(result).toBe(true)
    })

    it('should return false when profile does not exist', async () => {
        // Setup mock chain
        const maybeSingleMock = vi.fn().mockResolvedValue({ data: null, error: null })

        supabase.from.mockImplementation(() => ({
            select: () => ({
                eq: () => ({
                    maybeSingle: maybeSingleMock
                })
            })
        }))

        const result = await checkUserAccess('456')
        expect(result).toBe(false)
    })

    it('should return false when database error occurs', async () => {
        // Setup mock chain
        const maybeSingleMock = vi.fn().mockResolvedValue({ data: null, error: { message: 'DB Error' } })

        supabase.from.mockImplementation(() => ({
            select: () => ({
                eq: () => ({
                    maybeSingle: maybeSingleMock
                })
            })
        }))

        const result = await checkUserAccess('789')
        expect(result).toBe(false)
    })
})
