import { Link } from 'react-router-dom'
import Header from '../components/Header'

export default function AdminHelp({ session }) {
    return (
        <div className="dashboard-container">
            <Header session={session} />
            <div className="max-w-4xl mx-auto p-4 mt-6">
                <div className="mb-6">
                    <Link to="/admin" className="text-blue-400 hover:text-blue-300 text-sm flex items-center gap-1 mb-2">
                        <span>&larr;</span> Back to Admin Hub
                    </Link>
                    <h1 className="text-3xl font-bold">Admin Help & Architecture</h1>
                </div>

                <div className="space-y-6">
                    <section className="bg-slate-800 p-6 rounded-lg border border-slate-700">
                        <h2 className="text-xl font-bold text-white mb-2">Event Registration & Workflow</h2>
                        <ul className="list-disc pl-5 text-gray-300 space-y-2">
                            <li><strong>NOT_YET_OPEN:</strong> Events are generated up to two weeks ahead, but sign-ups are disabled.</li>
                            <li><strong>OPEN_FOR_ROSTER:</strong> Only users belonging to the `roster_user_group` can sign up. (They enter directly on the Waitlist if full).</li>
                            <li><strong>OPEN_FOR_RESERVES:</strong> Roster users can still sign up. Reserves (Tier 2 and 3) enter the `WAITLIST_HOLDING` queue. They are NOT placed in any particular order yet.</li>
                            <li><strong>PRELIMINARY_ORDERING:</strong> The Cron logic triggers and automatically randomizes Tier 2 and Tier 3 reserves, then assigns them empty slots or adds them to the Waitlist.</li>
                            <li><strong>FINAL_ORDERING:</strong> The Open Access period. Anyone can drop out, and Waitlist members are auto-promoted.</li>
                        </ul>
                    </section>

                    <section className="bg-slate-800 p-6 rounded-lg border border-slate-700">
                        <h2 className="text-xl font-bold text-white mb-2">Background Job (Cron)</h2>
                        <ul className="list-disc pl-5 text-gray-300 space-y-2">
                            <li>The scheduler runs daily to generate new events based on standard templates (`Event Types`).</li>
                            <li>A Cron job running closely analyzes upcoming event statuses. If an event crosses a threshold time, it will send out emails and trigger randomized waitlist assignment.</li>
                            <li>You can manually run this exact Cron job from the Admin Hub via the "Trigger Scheduler" button.</li>
                        </ul>
                    </section>

                    <section className="bg-slate-800 p-6 rounded-lg border border-slate-700">
                        <h2 className="text-xl font-bold text-white mb-2">Reference Documents</h2>
                        <p className="text-gray-400 mb-4">
                            If you need more details about the technical implementation, consult the provided Markdown instructions in the project repository:
                        </p>
                        <div className="flex gap-4">
                            <span className="bg-slate-700 text-gray-300 px-3 py-1 rounded font-mono text-sm">NEW_WORKFLOW_PLAN.md</span>
                            <span className="bg-slate-700 text-gray-300 px-3 py-1 rounded font-mono text-sm">ARCH.md</span>
                        </div>
                    </section>
                </div>
            </div>
        </div>
    )
}
