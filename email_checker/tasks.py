import imaplib
import email
from email.header import decode_header
from celery import shared_task
from .models import EmailMessage
import logging
from crudproject import settings

# Configure logger for the module
logger = logging.getLogger(__name__)


@shared_task
def check_new_emails():
    """
    Check for new unseen emails in the Gmail inbox and store them in the database.

    This function connects to the Gmail IMAP server, searches for unseen emails,
    processes each email, and stores relevant details in the EmailMessage model.

    Example:
        >>> check_new_emails.delay()
    """
    try:
        # Connect to the Gmail IMAP server using SSL
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        # Log in using the configured email and password
        mail.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

        logger.info("Connected to Gmail IMAP server.")

        # Select the inbox folder to search for emails
        mail.select('inbox')

        # Search for all unseen emails
        status, messages = mail.search(None, 'UNSEEN')
        # Split the resulting email IDs into a list
        email_ids = messages[0].split()

        # Check if there are any unseen emails
        if not email_ids:
            logger.info("No new emails.")
            return

        # Process each email, limiting to the first 10 unseen emails
        for e_id in email_ids[:10]:
            # Fetch the complete email message
            res, msg = mail.fetch(e_id, '(RFC822)')
            raw_email = msg[0][1]  # Get the raw email content

            # Parse the email using the email module
            msg = email.message_from_bytes(raw_email)
            # Decode the email subject
            subject, encoding = decode_header(msg['Subject'])[0]
            if isinstance(subject, bytes):
                # If the subject is in bytes, decode it to a string
                subject = subject.decode(encoding if encoding else 'utf-8')

            # Initialize the email body
            body = ""

            # Check if the email is multipart
            if msg.is_multipart():
                # Iterate through each part of the email
                for part in msg.walk():
                    # Get the content type of the part
                    content_type = part.get_content_type()
                    content_disposition = str(
                        part.get("Content-Disposition")
                    )

                    # Process only text/plain parts (ignore attachments)
                    if content_type == "text/plain" and 'attachment' not in content_disposition:
                        payload = part.get_payload(decode=True)
                        if payload:  # Ensure the payload is not None
                            body = payload.decode('utf-8', errors='ignore')
                            break  # No need to check further parts
            else:
                # If it's a single part email, decode the payload directly
                payload = msg.get_payload(decode=True)
                if payload:  # Ensure the payload is not None
                    body = payload.decode('utf-8', errors='ignore')

            # if not EmailMessage.objects.filter(
            #     body=body
            # ).exists():

            # Store the email details in the database
            EmailMessage.objects.create(
                subject=subject,
                from_email=msg['From'],
                to_email=msg['To'],
                body=body,
            )
            logger.info(f"Email processed: {subject} from {msg['From']}")

            # Mark the email as seen
            print(f" [___+++ Mail ${e_id} has been marked as SEEN +++___]")
            mail.store(e_id, '+FLAGS', '\\Seen')

            # else:
            #     logger.info(f"Duplicate body content skipped: {subject} from {msg['From']}")

        # Log out from the mail server
        mail.logout()

    except imaplib.IMAP4.error as e:
        # Log any IMAP errors
        logger.error(f"IMAP error: {e}")
    except Exception as e:
        # Log any other exceptions
        logger.error(f"An error occurred: {e}")
