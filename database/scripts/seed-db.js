import { createClient } from '@supabase/supabase-js'
import dotenv from 'dotenv'
import path from 'path'
import { fileURLToPath } from 'url'

// Load .env from parent directory
const __dirname = path.dirname(fileURLToPath(import.meta.url))
dotenv.config({ path: path.join(__dirname, '../.env') })

const supabaseUrl = process.env.VITE_SUPABASE_URL
const supabaseKey = process.env.VITE_SUPABASE_ANON_KEY
// NOTE: Ideally for admin tasks we'd use SERVICE_ROLE_KEY to bypass RLS, 
// but for this demo using ANON key and public access policies is a shortcut.
// If RLS blocks this, we'd need the user to provide the service role key or 
// we temporarily disable RLS. Given the schema.sql had "true" policies, this should work.

if (!supabaseUrl || !supabaseKey) {
    console.error("Missing credentials in .env")
    process.exit(1)
}

const supabase = createClient(supabaseUrl, supabaseKey)

async function seed() {
    console.log("Starting seed...")

    // 1. Create a User Group
    console.log("Creating User Group 'Basketball Regulars'...")
    const { data: group, error: groupError } = await supabase
        .from('user_groups')
        .insert({ name: 'Basketball Regulars' })
        .select()
        .single()

    if (groupError) {
        if (groupError.code === '23505') { // Unique violation
            console.log("Group already exists, skipping.")
        } else {
            console.error("Error creating group:", groupError)
        }
    } else {
        console.log("Created group:", group.id)
    }

    // 2. Create an Event
    console.log("Creating Event for next week...")

    const today = new Date()
    const nextWeek = new Date(today)
    nextWeek.setDate(today.getDate() + 7)
    nextWeek.setHours(18, 0, 0, 0) // 6 PM

    // Timings relative to event (just examples)
    const rosterOpen = new Date(nextWeek)
    rosterOpen.setDate(rosterOpen.getDate() - 6) // Opens 6 days before

    const waitlistOpen = new Date(nextWeek)
    waitlistOpen.setDate(waitlistOpen.getDate() - 5) // Opens 5 days before

    const reserveOpen = new Date(nextWeek)
    reserveOpen.setDate(reserveOpen.getDate() - 4) // Opens 4 days before

    const initialReserve = new Date(nextWeek)
    initialReserve.setDate(initialReserve.getDate() - 2) // 2 days before

    const finalReserve = new Date(nextWeek)
    finalReserve.setDate(finalReserve.getDate() - 1) // 1 day before

    const { data: event, error: eventError } = await supabase
        .from('events')
        .insert({
            name: 'Weekly Basketball',
            max_signups: 10,
            event_date: nextWeek.toISOString(),
            roster_sign_up_open: rosterOpen.toISOString(),
            waitlist_sign_up_open: waitlistOpen.toISOString(),
            reserve_sign_up_open: reserveOpen.toISOString(),
            initial_reserve_scheduling: initialReserve.toISOString(),
            final_reserve_scheduling: finalReserve.toISOString()
        })
        .select()
        .single()

    if (eventError) {
        console.error("Error creating event:", eventError)
    } else {
        console.log("Created event:", event.id)
    }

    console.log("Seed complete.")
}

seed()
