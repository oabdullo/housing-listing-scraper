#!/usr/bin/env python3
"""
Email test script to diagnose email sending issues
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_CONFIG
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_email():
    """Test email sending functionality"""
    print("📧 Testing Email Configuration")
    print("=" * 40)
    
    # Check if email password is set
    email_password = os.getenv('EMAIL_PASSWORD')
    if not email_password:
        print("❌ EMAIL_PASSWORD environment variable not set!")
        print("Please set it with: export EMAIL_PASSWORD='your_app_password'")
        return False
    
    print(f"✅ EMAIL_PASSWORD found (length: {len(email_password)})")
    print(f"📤 Sender: {EMAIL_CONFIG['sender_email']}")
    print(f"📥 Recipient: {EMAIL_CONFIG['recipient_email']}")
    print(f"🔗 SMTP Server: {EMAIL_CONFIG['smtp_server']}:{EMAIL_CONFIG['smtp_port']}")
    print()
    
    try:
        # Create test message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = EMAIL_CONFIG['recipient_email']
        msg['Subject'] = "Test Email from House Scraper"
        
        body = """
        This is a test email from your house listing scraper.
        
        If you receive this email, your email configuration is working correctly!
        
        The scraper will now be able to send you daily house listings.
        
        Best regards,
        House Listing Scraper
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        print("🔄 Connecting to Gmail SMTP server...")
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        
        print("🔄 Authenticating...")
        server.login(EMAIL_CONFIG['sender_email'], email_password)
        
        print("🔄 Sending email...")
        text = msg.as_string()
        server.sendmail(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['recipient_email'], text)
        server.quit()
        
        print("✅ Test email sent successfully!")
        print("Check your inbox (and spam folder) for the test email.")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("This usually means:")
        print("1. Your Gmail App Password is incorrect")
        print("2. 2-Factor Authentication is not enabled on your Gmail account")
        print("3. You're using your regular Gmail password instead of an App Password")
        return False
        
    except smtplib.SMTPRecipientsRefused as e:
        print(f"❌ Recipient email rejected: {e}")
        print("Check that the recipient email address is correct")
        return False
        
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_email()
    if not success:
        print("\n🔧 Troubleshooting Tips:")
        print("1. Make sure you have 2-Factor Authentication enabled on Gmail")
        print("2. Generate a new App Password at: https://myaccount.google.com/apppasswords")
        print("3. Use the 16-character App Password (not your regular password)")
        print("4. Check that the email addresses in config.py are correct")
        print("5. Make sure your internet connection is working")
