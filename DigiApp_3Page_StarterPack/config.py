import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24))
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    APP_URL = os.getenv('APP_URL', 'http://localhost:5000')
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
    
    # File Storage
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    DATA_FOLDER = os.getenv('DATA_FOLDER', 'data')
    INVOICE_FOLDER = os.getenv('INVOICE_FOLDER', 'invoices')
    
    # Payment Configuration
    PAYPAL_ME_LINK = os.getenv('PAYPAL_ME_LINK', 'https://paypal.me/Apps4Mybiz/5')
    STRIPE_TIER1_LINK = os.getenv('STRIPE_TIER1_LINK')
    STRIPE_TIER2_LINK = os.getenv('STRIPE_TIER2_LINK')
    STRIPE_TIER3_LINK = os.getenv('STRIPE_TIER3_LINK')
    
    # Email Configuration
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    SENDER_EMAIL = os.getenv('SENDER_EMAIL')
    
    # Support Group Settings
    SUPPORT_GROUP_EMAIL = os.getenv('SUPPORT_GROUP_EMAIL')
    SUPPORT_GROUP_PHONE = os.getenv('SUPPORT_GROUP_PHONE')
    
    # Security
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
    
    # Feature Flags
    ENABLE_WHATSAPP = os.getenv('ENABLE_WHATSAPP', 'true').lower() == 'true'
    ENABLE_IMESSAGE = os.getenv('ENABLE_IMESSAGE', 'true').lower() == 'true'
    ENABLE_VERIFICATION = os.getenv('ENABLE_VERIFICATION', 'true').lower() == 'true'
    ENABLE_SUPPORT_GROUP = os.getenv('ENABLE_SUPPORT_GROUP', 'true').lower() == 'true'
    ENABLE_AFFILIATE = os.getenv('ENABLE_AFFILIATE', 'true').lower() == 'true'

    @classmethod
    def validate_required_vars(cls):
        """Validate that all required environment variables are set."""
        required_vars = [
            'OPENAI_API_KEY',
            'TWILIO_ACCOUNT_SID',
            'TWILIO_AUTH_TOKEN',
            'TWILIO_PHONE_NUMBER',
            'SECRET_KEY',
            'PAYPAL_ME_LINK'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            ) 