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
                        <ul className="list-disc pl-5 text-gray-300 space-y-1">
                            <li>Found on the <strong>Events</strong> page.</li>
                            <li>Shows current status and active sign-up windows.</li>
                            <li>Lists all players currently signed up.</li>
                        </ul>
                    </section>

                    <section className="bg-slate-800 p-6 rounded-lg border border-slate-700">
                        <h2 className="text-xl font-bold text-blue-400 mb-2">2. Roster Sign-up Phase</h2>
                        <ul className="list-disc pl-5 text-gray-300 space-y-1">
                            <li><strong>Who:</strong> Roster members.</li>
                            <li>Sign up directly for the event or join waitlist if full.</li>
                        </ul>
                    </section>

                    <section className="bg-slate-800 p-6 rounded-lg border border-slate-700">
                        <h2 className="text-xl font-bold text-yellow-400 mb-2">3. Reserve Holding Phase</h2>
                        <ul className="list-disc pl-5 text-gray-300 space-y-1">
                            <li><strong>Who:</strong> Reserves.</li>
                            <li>Names added to the <strong>Holding Area</strong> (not first-come, first-served).</li>
                            <li>Once window ends, reserves are split into first and second priority.</li>
                            <li>System randomizes each priority group to determine final assignment order.</li>
                        </ul>
                    </section>

                    <section className="bg-slate-800 p-6 rounded-lg border border-slate-700">
                        <h2 className="text-xl font-bold text-emerald-400 mb-2">4. Preliminary & Final Ordering</h2>
                        <ul className="list-disc pl-5 text-gray-300 space-y-1">
                            <li>Holding area members moved to <strong>Event</strong> or <strong>Waitlist</strong> after randomization.</li>
                            <li>Open access phase follows: anyone can join the end of the waitlist.</li>
                            <li>Automatic promotion from waitlist if a spot opens up.</li>
                        </ul>
                    </section>

                    <section className="bg-slate-800 p-6 rounded-lg border border-slate-700 border-l-4 border-l-red-500">
                        <h2 className="text-xl font-bold text-red-400 mb-2">Removing Yourself</h2>
                        <p className="text-gray-300">
                            If you can no longer attend, <strong>remove yourself</strong> immediately. This enables automatic promotion and timely notification for others on the waitlist.
                        </p>
                    </section>
                </div>
            </div>
        </div>
    )
}
