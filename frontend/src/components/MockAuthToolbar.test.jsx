import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import MockAuthToolbar from '../components/MockAuthToolbar'

// Mock the environment variable
vi.stubGlobal('import.meta', { env: { VITE_USE_MOCK_AUTH: 'true' } })

// Mock Supabase Client using Promise.resolve to ensure 'then' exists
vi.mock('../supabaseClient', () => ({
    supabase: {
        auth: {
            getSession: () => Promise.resolve({ data: { session: null } }),
            signOut: () => Promise.resolve({})
        }
    }
}))

describe('MockAuthToolbar', () => {
    let originalLocation

    beforeEach(() => {
        // Mock window.location.reload
        originalLocation = window.location
        delete window.location
        window.location = { reload: vi.fn() }
    })

    afterEach(() => {
        vi.restoreAllMocks()
        window.location = originalLocation
    })

    it('renders closed by default', async () => {
        render(<MockAuthToolbar />)
        // Use regular expression to match partial text
        expect(screen.getByText(/Mock Auth/)).toBeInTheDocument()

        // Button with arrow
        expect(screen.getByText('▲')).toBeInTheDocument()
    })

    it('expands when clicked', async () => {
        render(<MockAuthToolbar />)
        const toggleBtn = screen.getByText('▲')
        fireEvent.click(toggleBtn)

        // Should show dropdowns now
        expect(screen.getByText('Current:')).toBeInTheDocument()
    })
})
