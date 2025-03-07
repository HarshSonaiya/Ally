from config.settings import settings
from ssl import create_default_context
from email.mime.text import MIMEText
from smtplib import SMTP
import markdown 

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_email(file_name: str, summary: str):
    try:
        summary_html = markdown.markdown(summary)

        # HTML email template
        email_content = f"""
            <html>
                <body>
                    <p>Dear Participant,</p>
                    <p>I hope this email finds you well.</p>
                    <p>Below is the summary of the file {file_name}:</p>
                    <blockquote style="border-left: 3px solid #ccc; padding-left: 10px; margin-left: 20px;">
                    <p>{summary_html}</p>
                    </blockquote>
                    <p>Thank you for your time and participation.</p>
                    <br>
                    <p>Best regards,</p>
                    <p><strong>Your Name</strong><br>
                    Meeting Coordinator<br>
                </body>
            </html>
        """

        # for participant in participants:

        logger.info("Preparing email content...")
        message = MIMEText(email_content, "html")
        message["Subject"] = "Metting Takeaways"
        message["From"] = settings.USERNAME
        message["To"] = "harshsonaiya.work@gmail.com"

        context = create_default_context()
        logger.info("Attempting to connect to SMTP server...")
        with SMTP(settings.HOST, settings.PORT) as server:
            server.ehlo()
            server.starttls(context=context)
            server.login(settings.USERNAME, settings.PASSWORD)
            logger.info("Connected to SMTP server")

            # Send email to all participants
            server.sendmail(
                from_addr=message["From"],
                to_addrs=message["To"],
                msg=message.as_string()
            )
            logger.info(f"Mail sent successfully to {message['To']}")
            server.quit()

        return {"message": "Mail sent successfully"}
    except Exception as e:
        raise e
    