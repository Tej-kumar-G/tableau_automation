import smtplib
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
        with smtplib.SMTP(mail_cfg['smtp_server'], int(mail_cfg['port'])) as server:
            server.starttls()
            # 🔐 Login with email and app password
            server.login(mail_cfg['mail_from'], mail_cfg['password'])
            server.sendmail(msg['From'], mail_cfg['mail_to'].split(','), msg.as_string())
            logger.info("✅ Email sent successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to send email: {e}")
