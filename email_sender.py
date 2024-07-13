import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(receiver_email, subject, body):
    # Your email configuration
    sender_email = "akshayaabk1908@gmail.com"
    sender_password = "dwmh kzdp jdgu iqke"
    
    # Create message container (Multipart)
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    
    # Attach body to email
    msg.attach(MIMEText(body, 'plain'))
    
    # Send the email via SMTP server
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
