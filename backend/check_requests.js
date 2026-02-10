
import { createClient } from '@supabase/supabase-js'
import dotenv from 'dotenv'
import path from 'path'
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.join(__dirname, '../frontend/.env') }) // Adjust path as needed

const supabaseUrl = process.env.VITE_SUPABASE_URL
const supabaseKey = process.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseKey) {
    console.error('Missing Supabase URL or Key in .env file')
    process.exit(1)
}

const supabase = createClient(supabaseUrl, supabaseKey)

async function checkRequests() {
    const { data, error } = await supabase
        .from('access_requests')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(5)

    if (error) {
        console.error('Error fetching requests:', error)
    } else {
        console.log('--- Latest 5 Access Requests ---')
        if (data.length === 0) {
            console.log("No requests found.")
        } else {
            data.forEach(req => {
                console.log(`Email: ${req.email}, Status: ${req.status}, Created: ${req.created_at}`)
            })
        }
    }
}

checkRequests()
