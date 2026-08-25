import os
from datetime import timedelta

class Config:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this-in-production')
    
    # SMTP Settings (for Email Notifications)
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.sendgrid.net")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "apikey")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "noreply@otsi-ess.com")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Supabase Configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://your-project.supabase.co')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'your-supabase-key')
    
    # CORS Configuration
    CORS_HEADERS = 'Content-Type'
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

    # MFA feature flag
    MFA_ENABLED = os.getenv('MFA_ENABLED', 'true').strip().lower() in ('1', 'true', 'yes', 'on')
    
    # Office Location (Hyderabad HQ)
    OFFICE_LAT = 17.4474
    OFFICE_LNG = 78.3762
    OFFICE_RADIUS_M = 300
    
    # Working hours
    WORKING_HOURS_PER_DAY = 8.5
    OFFICE_START_TIME = "09:00"
    OFFICE_END_TIME = "18:00"

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
