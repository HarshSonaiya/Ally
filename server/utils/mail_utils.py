from config.settings import settings
from ssl import create_default_context
from services.elasticsearch_service import ElasticsearchService
from email.mime.text import MIMEText
from smtplib import SMTP

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_email(workspace_name: str, file_id: str, elastic_service: ElasticsearchService):
    try:
        
        logger.info("Begin file retrieval from elastic search.")

        meeting_data = elastic_service.retrieve_from_elastic(workspace_name, file_id)
        transcript = meeting_data.get("transcript", "")  
        participants = meeting_data.get("participants", [])

        logger.info(f"Mail Transcript: {transcript}")
        logger.info(f"Mail Participants: {participants}")

        logger.info("Preparing email content...")
        message = MIMEText(transcript)
        message["Subject"] = "Metting Takeaways"
        message["From"] = settings.USERNAME

        context = create_default_context()
        logger.info("Attempting to connect to SMTP server...")
        with SMTP(settings.HOST,settings.PORT) as server:
            server.ehlo()
            server.starttls(context=context)
            server.login(settings.USERNAME, settings.PASSWORD)
            logger.info("Connecting to SMTP server established")
            for participant in participants:
                logger.info(f"Participant: {participant} and {type(participant)}")
                message["To"] = participant
                server.sendmail(
                    from_addr = message["From"], 
                    to_addrs = message["To"], 
                    msg = message.as_string()
                )
            logger.info(f"Mail sent successfully to {message['To']}")
            server.quit()
        return {"message": "Mail sent successfully"}
    except Exception as e:
        raise Exception 
    