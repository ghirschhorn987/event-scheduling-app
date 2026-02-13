import { createClient } from '@supabase/supabase-js'
import dotenv from 'dotenv'
import path from 'path'

dotenv.config({ path: 'backend/.env' })

const supabaseUrl = process.env.SUPABASE_URL
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY

const supabase = createClient(supabaseUrl, supabaseKey)

async function test() {
    try {
        const { data, error } = await supabase.rpc('exec_sql', { sql: 'SELECT 1' })
        if (error) {
            console.log("FAILED:", error)
        } else {
            console.log("SUCCESS: Result:", data)
        }
    } catch (e) {
        console.log("ERROR:", e)
    }
}

test()
