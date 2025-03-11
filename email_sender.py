import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import markdown

def send_email(sender: str, receiver: str, subject: str, content: str, smtp_user: str, smtp_password: str):
    """Send an email using Mailtrap SMTP with Markdown-formatted content."""
    try:
        logging.info("Converting Markdown content to HTML")
        html_content = markdown.markdown(content, extensions=['markdown.extensions.tables'])

        logging.info("Creating email message")
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = receiver

        msg.attach(MIMEText(content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        smtp_server = "sandbox.smtp.mailtrap.io"
        smtp_port = 2525

        logging.info("Connecting to SMTP server")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            logging.info("Logging in to SMTP server")
            server.login(smtp_user, smtp_password)

            logging.info("Sending email to %s", receiver)
            server.sendmail(sender, receiver, msg.as_string())

        logging.info("Email sent successfully")
        with open("email_report.log", "a") as f:
            f.write(f"{logging.getLogger().handlers[0].formatter.format(logging.makeLogRecord({'asctime': logging.Formatter().formatTime(logging.makeLogRecord({}))}))} - INFO - Email sent to {receiver}\n")
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")
        raise