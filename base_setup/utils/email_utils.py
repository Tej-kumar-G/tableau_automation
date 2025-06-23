import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger('tableau_automation')


def send_email(subject, body_html, config):
    mail_cfg = config['email']
    msg = MIMEMultipart()
    msg['To'] = mail_cfg['mail_to']
    msg['From'] = mail_cfg['mail_from']
    msg['Subject'] = subject
    msg.attach(MIMEText(body_html, 'html'))

    try:
        start = time.perf_counter()
        with smtplib.SMTP(mail_cfg['smtp_server'], int(mail_cfg['port'])) as server:
            server.set_debuglevel(1)  # For verbose output
            server.starttls()
            server.login(mail_cfg['mail_from'], mail_cfg['password'])
            server.sendmail(msg['From'], mail_cfg['mail_to'].split(','), msg.as_string())
            elapsed = time.perf_counter() - start
            logger.info(f"✅ Email sent successfully in {elapsed:.2f} seconds.")
    except Exception as e:
        logger.error(f"❌ Failed to send email: {e}")
