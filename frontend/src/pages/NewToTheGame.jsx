import { Link } from 'react-router-dom'

export default function NewToTheGame() {
    return (
        <div className="login-card">
            <h1 className="text-2xl font-bold mb-4">New To The Game?</h1>
            <p className="mb-4 text-gray-300">
                Welcome! If you are interested in joining Beth Am Basketball, please follow these steps to get started.
            </p>

            <div className="bg-slate-800 p-4 rounded-lg mb-6 border border-slate-700">
                <h2 className="text-xl font-bold mb-2 text-white">Step 1: Request Access</h2>
                <p className="text-sm text-gray-400 mb-3">
                    First, you need to submit a request to join. Our administrators will review your request.
                </p>
                <Link to="/request-access" className="primary-btn inline-block text-center mt-2">
                    Request Access
                </Link>
            </div>

            <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
                <h2 className="text-xl font-bold mb-2 text-white">Step 2: Create Account</h2>
                <p className="text-sm text-gray-400 mb-3">
                    Once your request is approved by an administrator, you can come back and create your account to sign up for games.
                </p>
                <Link to="/signup" className="primary-btn inline-block text-center mt-2" style={{ backgroundColor: '#4f46e5' }}>
                    Create Your Account
                </Link>
            </div>

            <div className="mt-8 text-center">
                <Link to="/login" className="text-blue-400 hover:underline">
                    &larr; Back to Login
                </Link>
            </div>
        </div>
    )
}
