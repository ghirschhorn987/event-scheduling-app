import { supabase } from '../supabaseClient'

/**
 * Checks if a user has a valid profile in the system.
 * Returns true if access is allowed, false otherwise.
 * 
 * @param {string} userId - The Supabase auth user ID
 * @returns {Promise<boolean>}
 */
export const checkUserAccess = async (userId) => {
    try {
        const { data, error } = await supabase
            .from('profiles')
            .select('id')
            .eq('auth_user_id', userId)
            .maybeSingle()

        if (error) {
            console.error('Error checking user access:', error)
            return false
        }

        // If data exists, the user has a profile and is "registered/approved"
        return !!data
    } catch (err) {
        console.error('Unexpected error checking access:', err)
        return false
    }
}
