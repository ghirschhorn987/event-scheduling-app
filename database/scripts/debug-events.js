import { createClient } from '@supabase/supabase-js'
import dotenv from 'dotenv'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
dotenv.config({ path: path.join(__dirname, '../.env') })

const supabaseUrl = process.env.VITE_SUPABASE_URL
const supabaseKey = process.env.VITE_SUPABASE_ANON_KEY

const supabase = createClient(supabaseUrl, supabaseKey)

async function checkEvents() {
    console.log("Checking events table...")

    const { data, error } = await supabase
        .from('events')
        .select('*')

    if (error) {
        console.error("Error fetching events:", error)
    } else {
        console.log(`Found ${data.length} events:`)
        console.log(JSON.stringify(data, null, 2))
    }
}

checkEvents()
