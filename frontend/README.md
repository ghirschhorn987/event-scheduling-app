# Event Scheduling App

A React + Supabase application for managing community event signups.

## Setup

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Supabase Setup**
   - Create a new project at [Supabase](https://supabase.com).
   - Go to the **SQL Editor** and run the contents of `schema.sql` to create tables and policies.
   - Go to **Authentication -> Providers** and enable **Google**.
   - Copy `.env.example` to `.env` and enter your project URL and Anon Key.

3. **Run Locally**
   ```bash
   npm run dev
   ```

## Logic & Features

The app handles complex sign-up logic based on user membership and time windows:

- **Members**: Direct access to Roster (if open) or Waitlist (if full).
- **Guests (Non-Members)**:
  - **Before Reserve Open**: Sign up blocked.
  - **Reserve Window 1 (Holding)**: Added to Holding Area with `hyphen` sequence.
  - **Reserve Window 2 (Initial Scheduling)**: Added to Holding Area with sequence number.
  - **After Final Scheduling**: Added to Main Roster or Waitlist normally.

## Tech Stack
- React (Vite)
- Supabase (Auth & Database)
- Vanilla CSS (Dark Mode)
