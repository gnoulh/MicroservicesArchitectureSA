import requests
from flask import current_app
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class EmailService:
    def __init__(self, config):
        api_key = config.get('SENDGRID_API_KEY')
        if not api_key:
            raise ValueError("SENDGRID_API_KEY not found in config")
        self.client = SendGridAPIClient(api_key=api_key)
    
    def send_email(self, user_id: str, subject: str, content: str, metadata: dict = None) -> bool:
        """Send email notification"""
        try:
            # Get user email from user service
            user_email = self._get_user_email(user_id)
            if not user_email:
                return False
            
            if self.client:
                # Use SendGrid
                message = Mail(
                    from_email=current_app.config['FROM_EMAIL'],
                    to_emails=user_email,
                    subject=subject,
                    html_content=self._format_email_content(content, metadata)
                )
                
                response = self.client.send(message)
                return response.status_code < 400
            else:
                # Log email (development mode)
                print(f"EMAIL TO {user_email}: {subject}\n{content}")
                return True
                
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False
    
    def _get_user_email(self, user_id: str) -> str:
        """Get user email from user service"""
        try:
            response = requests.get(
                f"{current_app.config['USER_SERVICE_URL']}/users/{user_id}",
                timeout=5
            )
            if response.status_code == 200:
                user_data = response.json()
                return user_data.get('email')
        except Exception as e:
            print(f"Failed to get user email: {e}")
        
        return None
    
    def _format_email_content(self, content: str, metadata: dict = None) -> str:
        """Format email content with HTML"""
        html_content = f"""
        <html>
        <body>
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #333;">Todo App Notification</h2>
                <div style="background-color: #f5f5f5; padding: 20px; border-radius: 5px;">
                    {content}
                </div>
                <p style="color: #666; font-size: 12px; margin-top: 20px;">
                    You received this notification because you have notifications enabled for your Todo App account.
                </p>
            </div>
        </body>
        </html>
        """
        return html_content