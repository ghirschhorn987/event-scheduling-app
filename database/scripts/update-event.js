import { createClient } from '@supabase/supabase-js'
import dotenv from 'dotenv'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
dotenv.config({ path: path.join(__dirname, '../.env') })

const supabaseUrl = process.env.VITE_SUPABASE_URL
const supabaseKey = process.env.VITE_SUPABASE_ANON_KEY

const supabase = createClient(supabaseUrl, supabaseKey)

async function updateEvent() {
    console.log("Updating Event timings...")

    const today = new Date()
    const yesterday = new Date(today)
    yesterday.setDate(today.getDate() - 1)

    const tomorrow = new Date(today)
    tomorrow.setDate(today.getDate() + 1)

    const { data: events } = await supabase.from('events').select('*').limit(1)
    if (!events || events.length === 0) {
        console.log("No event found.")
        return
    }
    const eventId = events[0].id

    const { error } = await supabase
        .from('events')
        .update({
            roster_sign_up_open: yesterday.toISOString(), // OPEN for members
            reserve_sign_up_open: tomorrow.toISOString(), // CLOSED for guests
        })
        .eq('id', eventId)

    if (error) {
        console.error("Error updating event:", error)
    } else {
        console.log("Event updated: Roster OPEN, Reserve CLOSED")
    }
}

updateEvent()
