import smtplib
import os
from dotenv import load_dotenv

# Load environment variables from .flaskenv
load_dotenv('.flaskenv')

email = os.getenv('EMAIL_USER')
password = os.getenv('EMAIL_PASS')
print(password)

print(f"Email: {email}")
print(f"Password: {'*' * len(password) if password else 'Not set'}")

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
   
    if not email or not password:
        raise ValueError("EMAIL_USER or EMAIL_PASS environment variables are not set.")
   
    server.login(email, password)
    print("Logged in successfully!")
    server.quit()
except Exception as e:
    print(f"Error: {str(e)}")