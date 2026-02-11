
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
        subject = "Welcome to Skeddle - Access Granted"
        login_link = "https://skeddle.club/login"
        html = f"""
        <html>
            <body>
                <p>Hi {name},</p>
                <p>Good news! Your request to join Skeddle has been approved.</p>
                <p>You can now log in and sign up for events.</p>
                <p><a href="{login_link}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Log In to Skeddle</a></p>
                <br>
                <p>Welcome aboard,</p>
                <p>The Skeddle Team</p>
            </body>
        </html>
        """
        return self._send(to_email, subject, html)

email_service = EmailService()
