import requests
from flask import current_app
from twilio.rest import Client

class SMSService:
    def __init__(self, config):
        self.sid = config.get('TWILIO_ACCOUNT_SID')
        self.token = config.get('TWILIO_AUTH_TOKEN')

        if not self.sid or not self.token:
            raise ValueError("Twilio credentials not found in config")
    
    def send_sms(self, user_id: str, message: str) -> bool:
        """Send SMS notification"""
        try:
            # Get user phone from user service
            user_phone = self._get_user_phone(user_id)
            if not user_phone:
                return False
            
            if self.client:
                # Use Twilio
                message = self.client.messages.create(
                    body=f"Todo App: {message}",
                    from_=current_app.config['TWILIO_PHONE_NUMBER'],
                    to=user_phone
                )
                return True
            else:
                # Log SMS (development mode)
                print(f"SMS TO {user_phone}: {message}")
                return True
                
        except Exception as e:
            print(f"SMS sending failed: {e}")
            return False
    
    def _get_user_phone(self, user_id: str) -> str:
        """Get user phone from user service"""
        try:
            response = requests.get(
                f"{current_app.config['USER_SERVICE_URL']}/users/{user_id}",
                timeout=5
            )
            if response.status_code == 200:
                user_data = response.json()
                return user_data.get('phone')
        except Exception as e:
            print(f"Failed to get user phone: {e}")
        
        return None