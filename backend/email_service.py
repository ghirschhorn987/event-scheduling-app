
import os
import resend

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")

class EmailService:
    def __init__(self):
        if RESEND_API_KEY:
            resend.api_key = RESEND_API_KEY
        else:
            print("WARNING: RESEND_API_KEY not set. Email sending will be skipped (or mocked).")

    def _send(self, to_email: str, subject: str, html_content: str):
        """
        Internal wrapper to send email via Resend if key exists, else print mock.
        """
        if not RESEND_API_KEY:
            print(f"--- MOCK EMAIL ---")
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"Body: {html_content[:100]}...")
            print(f"------------------")
            return {"id": "mock-email-id"}

        try:
            params = {
                "from": "Skeddle <support@skeddle.club>", # Updated to verified domain
                "to": [to_email],
                "subject": subject,
                "html": html_content,
            }
            email = resend.Emails.send(params)
            return email
        except Exception as e:
            print(f"Error sending email to {to_email}: {e}")
            return None

    def send_user_acknowledgement(self, to_email: str, name: str):
        subject = "Registration Request Received - Skeddle"
        html = f"""
        <html>
            <body>
                <p>Hi {name},</p>
                <p>We have received your request to register for the Skeddle App.</p>
                <p>Please wait for a reply. If you do not hear back within 48 hours, please contact <a href="mailto:support@skeddle.club">support@skeddle.club</a>.</p>
                <br>
                <p>Best regards,</p>
                <p>The Skeddle Team</p>
            </body>
        </html>
        """
        return self._send(to_email, subject, html)

    def send_admin_notification(self, request_data: dict):
        admin_email = "support@skeddle.club"
        subject = f"New Registration Request: {request_data.get('full_name', 'Unknown')}"
        
        # Link to admin dashboard (assuming localhost or deployed url, let's use a generic relative path for now or just text)
        admin_link = "https://skeddle.club/admin" # Updated to production URL

        html = f"""
        <html>
            <body>
                <h2>New Registration Request</h2>
                <p><strong>Name:</strong> {request_data.get('full_name')}</p>
                <p><strong>Email:</strong> {request_data.get('email')}</p>
                <p><strong>Affiliation:</strong> {request_data.get('affiliation')}</p>
                <p><strong>Referral:</strong> {request_data.get('referral') or 'N/A'}</p>
                <br>
                <p><a href="{admin_link}">View in Admin Dashboard</a></p>
            </body>
        </html>
        """
        return self._send(admin_email, subject, html)

    def send_rejection_reason(self, to_email: str, reason: str):
        subject = "Update on your Registration Request - Skeddle"
        html = f"""
        <html>
            <body>
                <p>Hello,</p>
                <p>Thank you for your interest in Skeddle.</p>
                <p>Unfortunately, we are unable to approve your registration request at this time.</p>
                <p><strong>Reason:</strong></p>
                <blockquote style="background: #f9f9f9; padding: 10px; border-left: 3px solid #ccc;">
                    {reason}
                </blockquote>
                <br>
                <p>Best regards,</p>
                <p>The Skeddle Team</p>
            </body>
        </html>
        """
        return self._send(to_email, subject, html)

    def send_more_info_request(self, to_email: str, message: str):
        subject = "More Information Needed - Skeddle"
        html = f"""
        <html>
            <body>
                <p>Hello,</p>
                <p>We received your registration request, but we need a bit more information before we can proceed.</p>
                <p><strong>Message from Admin:</strong></p>
                <blockquote style="background: #eef9fd; padding: 10px; border-left: 3px solid #2196f3;">
                    {message}
                </blockquote>
                <p>Please reply to this email with the requested details.</p>
                <br>
                <p>Best regards,</p>
                <p>The Skeddle Team</p>
            </body>
        </html>
        """
        return self._send(to_email, subject, html)

    def send_access_granted(self, to_email: str, name: str):
        subject = "Welcome to Skeddle - Access Approved"
        signup_link = "https://skeddle.club/signup"
        html = f"""
        <html>
            <body style="font-family: sans-serif; color: #333; line-height: 1.5;">
                <p>Hi {name},</p>
                <p>Good news! Your request to join Skeddle has been approved.</p>
                <p>You can now create your account to start signing up for events.</p>
                
                <p><a href="{signup_link}" style="background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">Create Your Account</a></p>
                
                <div style="margin-top: 30px; padding: 20px; background-color: #f9f9f9; border-radius: 8px; border: 1px solid #eee;">
                    <h3 style="margin-top: 0; color: #444;">Choose your sign-up method:</h3>
                    
                    <div style="margin-bottom: 20px;">
                        <strong style="color: #222;">Option 1: Site-Specific Password</strong>
                        <p style="margin: 5px 0; color: #555; font-size: 14px;">
                            Create a dedicated password for this site. It is encrypted and remains private; 
                            the system never sees your actual password. It can't be retrieved, only reset if forgotten.
                        </p>
                    </div>
                    
                    <div>
                        <strong style="color: #222;">Option 2: Google Authentication</strong>
                        <p style="margin: 5px 0; color: #555; font-size: 14px;">
                            Use your Google account to sign in securely without creating a new password. 
                            Google validates your identity, and the system never sees your credentials.
                        </p>
                    </div>
                </div>

                <p style="margin-top: 30px;">Welcome aboard,</p>
                <p><strong>The Skeddle Team</strong></p>
            </body>
        </html>
        """
        return self._send(to_email, subject, html)

email_service = EmailService()
