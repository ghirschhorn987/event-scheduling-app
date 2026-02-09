import { useState } from 'react'
import { Link } from 'react-router-dom'

const RequestAccess = () => {
    const [formData, setFormData] = useState({
        full_name: '',
        email: '',
    })

    // New State for improved questions
    const [isAffiliated, setIsAffiliated] = useState(null) // true, false, or null (unanswered)
    const [selectedAffiliations, setSelectedAffiliations] = useState([])
    const [otherAffiliation, setOtherAffiliation] = useState('')
    const [referralAnswer, setReferralAnswer] = useState('')

    const [status, setStatus] = useState('idle') // idle, submitting, success, error
    const [errorMsg, setErrorMsg] = useState('')

    const AFFILIATION_OPTIONS = [
        "Beth Am member",
        "Pressman parent",
        "Pressman alumni",
        "Beth Am / Pressman staff",
        "Other"
    ]

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value })
    }

    const handleAffiliationChange = (option) => {
        if (selectedAffiliations.includes(option)) {
            setSelectedAffiliations(selectedAffiliations.filter(item => item !== option))
        } else {
            setSelectedAffiliations([...selectedAffiliations, option])
        }
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setStatus('submitting')
        setErrorMsg('')

        // Construct final payload
        let finalAffiliation = ''
        let finalReferral = ''

        if (isAffiliated === true) {
            // Combine selected options
            let affiliations = [...selectedAffiliations]

            // If "Other" is selected, append the text
            if (affiliations.includes("Other") && otherAffiliation.trim()) {
                // Remove the generic "Other" and add the specific text or format it?
                // Plan says: "Pressman parent, Other: Donated recently"
                // So let's keep "Other" but maybe append text? 
                // Let's just append the other text to the list for simplicity in constructing string
                // Actually better: filter out "Other" string and add "Other: {text}"
                affiliations = affiliations.filter(a => a !== "Other")
                affiliations.push(`Other: ${otherAffiliation}`)
            }

            finalAffiliation = affiliations.join(", ")
            // validation
            if (!finalAffiliation) {
                setErrorMsg("Please select at least one affiliation option.")
                setStatus('idle')
                return
            }
        } else if (isAffiliated === false) {
            finalAffiliation = "Not Affiliated" // or leave empty? Database usually expects something if NOT NULL. 
            // DB Schema: affiliation TEXT NOT NULL. So we must provide something.
            finalReferral = referralAnswer

            if (!referralAnswer.trim()) {
                setErrorMsg("Please tell us how you found out about the game.")
                setStatus('idle')
                return
            }
        } else {
            setErrorMsg("Please answer the affiliation question.")
            setStatus('idle')
            return
        }

        const payload = {
            full_name: formData.full_name,
            email: formData.email,
            affiliation: finalAffiliation,
            referral: finalReferral
        }

        try {
            const res = await fetch('/api/request-access', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
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
        <div className="auth-form-container" style={{ maxWidth: '600px' }}> {/* Slightly wider for new qs */}
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

                {/* New Affiliation Question */}
                <div className="form-group question-section">
                    <label className="question-label">
                        Are you affiliated with Temple Beth Am or Pressman Academy? <br />
                        <span className="field-hint">(e.g. member, parent, alumni, staff, etc.)</span>
                    </label>

                    <div className="radio-group">
                        <label className={`radio-option ${isAffiliated === true ? 'selected' : ''}`}>
                            <input
                                type="radio"
                                name="isAffiliated"
                                checked={isAffiliated === true}
                                onChange={() => setIsAffiliated(true)}
                            />
                            Yes
                        </label>
                        <label className={`radio-option ${isAffiliated === false ? 'selected' : ''}`}>
                            <input
                                type="radio"
                                name="isAffiliated"
                                checked={isAffiliated === false}
                                onChange={() => setIsAffiliated(false)}
                            />
                            No
                        </label>
                    </div>
                </div>

                {/* Conditional Sections */}
                {isAffiliated === true && (
                    <div className="form-group sub-section">
                        <label>Please check all that apply:</label>
                        <div className="checkbox-group">
                            {AFFILIATION_OPTIONS.map(option => (
                                <label key={option} className="checkbox-option">
                                    <input
                                        type="checkbox"
                                        checked={selectedAffiliations.includes(option)}
                                        onChange={() => handleAffiliationChange(option)}
                                    />
                                    {option}
                                </label>
                            ))}
                        </div>

                        {selectedAffiliations.includes("Other") && (
                            <div className="form-group slide-in">
                                <label>Please explain:</label>
                                <input
                                    type="text"
                                    value={otherAffiliation}
                                    onChange={(e) => setOtherAffiliation(e.target.value)}
                                    placeholder="Tell us about your connection..."
                                    required
                                />
                            </div>
                        )}
                    </div>
                )}

                {isAffiliated === false && (
                    <div className="form-group sub-section slide-in">
                        <label>How did you find about this game?</label>
                        <input
                            type="text"
                            value={referralAnswer}
                            onChange={(e) => setReferralAnswer(e.target.value)}
                            placeholder="e.g. A friend, Google, etc."
                            required
                        />
                    </div>
                )}

                <button type="submit" disabled={status === 'submitting'} className="submit-btn">
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
