import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import markdown

def send_email(sender: str, receiver: str, subject: str, content: str, smtp_user: str, smtp_password: str):
    try:
        logging.info("Converting Markdown content to HTML")
        # Add 'extra' extension to handle numbered lists properly
        html_content = markdown.markdown(content, extensions=['markdown.extensions.tables', 'markdown.extensions.extra', 'markdown.extensions.nl2br'])

        # Wrap the HTML content in a styled template with the logo and confidentiality warning
        styled_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f5f5f5;
                }}
                .email-container {{
                    max-width: 600px;
                    margin: 20px auto;
                    background-color: #fff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }}
                .logo {{
                    display: block;
                    margin: 0 auto 20px auto;
                    width: 150px;
                    height: auto;
                }}
                h3 {{
                    color: #2c3e50;
                    margin-top: 20px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 10px;
                    text-align: left;
                }}
                th {{
                    background-color: #f4f4f4;
                    color: #2c3e50;
                    font-weight: bold;
                }}
                td {{
                    background-color: #fff;
                }}
                tr:nth-child(odd) td {{
                    background-color: #f9f9f9;
                }}
                p, li {{
                    line-height: 1.6;
                    margin: 10px 0;
                }}
                ol {{
                    padding-left: 20px;
                }}
                .separator {{
                    margin: 20px 0;
                    border-top: 1px solid #ddd;
                    padding-top: 10px;
                    font-style: italic;
                    color: #666;
                }}
                .confidentiality {{
                    margin-top: 30px;
                    padding: 10px;
                    border-top: 2px solid #e74c3c;
                    font-size: 12px;
                    color: #e74c3c;
                    text-align: center;
                    font-style: italic;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <img src="https://www.pngplay.com/wp-content/uploads/13/Levis-Transparent-File.png" alt="Levi's Logo" class="logo">
                {html_content}
                <div class="confidentiality">
                    <p>CONFIDENTIAL: This email contains proprietary information intended solely for the recipients listed. Unauthorized distribution or disclosure is prohibited.</p>
                </div>
            </div>
        </body>
        </html>
        """

        logging.info("Creating email message")
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = receiver

        msg.attach(MIMEText(styled_html, "html"))

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
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")
        raise