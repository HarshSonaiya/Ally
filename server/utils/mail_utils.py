from config.settings import settings
from ssl import create_default_context
from services.elasticsearch_service import ElasticsearchService
from email.mime.text import MIMEText
from smtplib import SMTP

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_email(workspace_name: str, file_id: str, summary: str, elastic_service: ElasticsearchService):
    try:
        
        logger.info("Begin file retrieval from elastic search.")

        meeting_data = elastic_service.retrieve_from_elastic(workspace_name, file_id)
        filename = meeting_data.get("filename")
        participants = meeting_data.get("participants", [])

        logger.info(f"Mail Summary: {summary}")
        logger.info(f"Mail Participants: {participants}")
        
        # HTML email template
        email_content = f"""
            <html>
                <body>
                    <p>Dear Participant,</p>
                    <p>I hope this email finds you well.</p>
                    <p>Below is the summary of the file {filename}:</p>
                    <blockquote style="border-left: 3px solid #ccc; padding-left: 10px; margin-left: 20px;">
                    <p>{summary}</p>
                    </blockquote>
                    <p>Thank you for your time and participation.</p>
                    <br>
                    <p>Best regards,</p>
                    <p><strong>Your Name</strong><br>
                    Meeting Coordinator<br>
                    <a href="mailto:{participants[0]}">{participants[0]}</a></p>
                </body>
            </html>
        """

        for participant in participants:

            logger.info("Preparing email content...")
            message = MIMEText(email_content, "html")
            message["Subject"] = "Metting Takeaways"
            message["From"] = settings.USERNAME
            message["To"] = participant

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
    