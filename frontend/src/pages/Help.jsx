import Header from '../components/Header'

export default function Help({ session }) {
    return (
        <div className="dashboard-container">
            <Header session={session} />
            <div className="max-w-4xl mx-auto p-4 mt-6">
                <h1 className="text-3xl font-bold mb-6">How Skeddle Works</h1>

                <div className="space-y-6">
                    <section className="bg-slate-800 p-6 rounded-lg border border-slate-700">
                        <h2 className="text-xl font-bold text-white mb-2">1. Event Visibility</h2>
                        <ul className="list-disc pl-5 text-gray-300 space-y-2">
                            <li>Events are generated automatically and appear under the <strong>Events</strong> page.</li>
                            <li>You can see the status of the event, indicating who is currently allowed to sign up.</li>
                        </ul>
                    </section>

                    <section className="bg-slate-800 p-6 rounded-lg border border-slate-700">
                        <h2 className="text-xl font-bold text-blue-400 mb-2">2. Roster Sign-up Phase</h2>
                        <ul className="list-disc pl-5 text-gray-300 space-y-2">
                            <li><strong>Who:</strong> Tier 1 (Roster Members)</li>
                            <li>When the event first opens, only core roster members can sign up directly to the main Event List.</li>
                            <li>If the main list fills up, roster members can still join the Waitlist.</li>
                        </ul>
                    </section>

                    <section className="bg-slate-800 p-6 rounded-lg border border-slate-700">
                        <h2 className="text-xl font-bold text-yellow-400 mb-2">3. Reserve Holding Phase</h2>
                        <ul className="list-disc pl-5 text-gray-300 space-y-2">
                            <li><strong>Who:</strong> Tier 2 & Tier 3 (Reserves)</li>
                            <li>When the reserve window opens, reserves can add themselves to the <strong>Holding Area</strong>.</li>
                            <li>This is not a first-come, first-served queue! All names sit in the holding area until the system randomly shuffles them at the end of the window.</li>
                            <li>Tier 2 members are randomized and placed first, followed by Tier 3 members.</li>
                        </ul>
                    </section>

                    <section className="bg-slate-800 p-6 rounded-lg border border-slate-700">
                        <h2 className="text-xl font-bold text-emerald-400 mb-2">4. Preliminary & Final Ordering</h2>
                        <ul className="list-disc pl-5 text-gray-300 space-y-2">
                            <li>Once the holding period ends, the system assigns everyone in the holding area to either the main <strong>Event</strong> or the <strong>Waitlist</strong>.</li>
                            <li>From this point on, it is an <strong>Open Access</strong> phase. Anyone can sign up, and they are added to the end of the waitlist on a first-come, first-served basis.</li>
                            <li>If a player on the main list drops out, the first person on the waitlist is automatically promoted.</li>
                        </ul>
                    </section>

                    <section className="bg-slate-800 p-6 rounded-lg border border-slate-700 border-l-4 border-l-red-500">
                        <h2 className="text-xl font-bold text-red-400 mb-2">Important Rule: Please Drop Out Early!</h2>
                        <p className="text-gray-300">
                            If you sign up but later realize you cannot attend, <strong>you MUST remove yourself</strong> from the list as soon as possible. This allows the system to automatically promote the next person on the waitlist and notify them in time.
                        </p>
                    </section>
                </div>
            </div>
        </div>
    )
}
