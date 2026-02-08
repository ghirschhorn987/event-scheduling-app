import { useState } from 'react'
import { Link } from 'react-router-dom'

const RequestAccess = () => {
    const [formData, setFormData] = useState({
        full_name: '',
        email: '',
        affiliation: '',
        referral: ''
    })
    const [status, setStatus] = useState('idle') // idle, submitting, success, error
    const [errorMsg, setErrorMsg] = useState('')

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value })
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setStatus('submitting')
        setErrorMsg('')

        try {
            const res = await fetch('/api/request-access', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            })

            const data = await res.json()

            if (!res.ok) {
                throw new Error(data.detail || 'Failed to submit request')
            }

            setStatus('success')
        } catch (err) {
            console.error(err)
            setStatus('error')
            setErrorMsg(err.message)
        }
    }

    if (status === 'success') {
        return (
            <div className="auth-form-container">
                <h2>Request Received</h2>
                <p>Thank you for requesting access!</p>
                <p>Your request has been submitted to the administrators.</p>
                <p>You will receive an email once your request has been reviewed.</p>
                <Link to="/login" className="back-link">Back to Login</Link>
            </div>
        )
    }

    return (
        <div className="auth-form-container">
            <h2>Request Access</h2>
            <p className="auth-subtitle">Join the Pickleball Scheduling App</p>

            {status === 'error' && <div className="error-message">{errorMsg}</div>}

            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label>Full Name</label>
                    <input
                        type="text"
                        name="full_name"
                        value={formData.full_name}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className="form-group">
                    <label>Email Address</label>
                    <input
                        type="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className="form-group">
                    <label>Affiliation (Temple Beth Am / Pressman)</label>
                    <p className="field-hint">e.g. Member, Parent, Alumni, Staff</p>
                    <input
                        type="text"
                        name="affiliation"
                        value={formData.affiliation}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className="form-group">
                    <label>Referral (If not a member)</label>
                    <p className="field-hint">Who referred you to the game?</p>
                    <input
                        type="text"
                        name="referral"
                        value={formData.referral}
                        onChange={handleChange}
                    />
                </div>

                <button type="submit" disabled={status === 'submitting'}>
                    {status === 'submitting' ? 'Submitting...' : 'Submit Request'}
                </button>
            </form>

            <div className="auth-links">
                <Link to="/login">Already have an account? Login</Link>
            </div>
        </div>
    )
}

export default RequestAccess
