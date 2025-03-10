import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from markdown2 import markdown

def send_email(sender: str, receiver: str, subject: str, content: str):
    """
    Sends an email using SMTP with the given sender, receiver, subject, and content.
    Content can be written in Markdown format.
    """
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        logging.info("Converting Markdown content to HTML")
        html_content = markdown(content)
        
        logging.info("Creating email message")
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = receiver
        
        msg.attach(MIMEText(content, "plain"))
        msg.attach(MIMEText(html_content, "html"))
        
        smtp_server = "sandbox.smtp.mailtrap.io"
        smtp_port = 2525
        smtp_user = ""
        smtp_password = ""
        
        logging.info("Connecting to SMTP server")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            logging.info("Logging in to SMTP server")
            server.login(smtp_user, smtp_password)
            
            logging.info("Sending email to %s", receiver)
            server.sendmail(sender, receiver, msg.as_string())
        
        logging.info("Email sent successfully")
    except Exception as e:
        logging.error("Failed to send email: %s", str(e))