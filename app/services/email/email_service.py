import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Сервис для отправки писем через SMTP"""
    
    def __init__(self):
        self.smtp_server = "smtp.mail.ru"
        self.smtp_port = 465
        self.sender_email = settings.SMPT_MAIL
        self.sender_password = settings.SMTP_MAIL_PASSWORD
    
    def send_password_email(self, to_email: str, user_login: str, password: str) -> bool:
        """
        Отправить письмо с новым паролем при создании пользователя
        
        Args:
            to_email: Email адрес получателя
            user_login: Логин пользователя
            password: Сгенерированный пароль
            
        Returns:
            True если письмо отправлено успешно, False иначе
        """
        if not self.sender_email or not self.sender_password:
            logger.warning("SMTP credentials not configured, skipping email send")
            return False
        
        try:
            # Создаём сообщение
            message = MIMEMultipart("alternative")
            message["Subject"] = "Ваш пароль для входа в InfoCenter"
            message["From"] = self.sender_email
            message["To"] = to_email
            
            # Текстовая версия письма
            text = f"""
Добро пожаловать в InfoCenter!

Ваши учётные данные:
Логин: {user_login}
Пароль: {password}

Вы можете изменить пароль в личном кабинете после первого входа.

С уважением,
Администратор InfoCenter
"""
            
            # HTML версия письма (более красивая)
            html = f"""
<html>
  <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px;">
      <h2 style="color: #333; text-align: center;">Добро пожаловать в InfoCenter!</h2>
      
      <p style="color: #666; font-size: 14px;">Ваши учётные данные для входа:</p>
      
      <div style="background-color: #f9f9f9; padding: 15px; border-left: 4px solid #0066cc; margin: 20px 0;">
        <p style="margin: 5px 0;"><strong>Логин:</strong> {user_login}</p>
        <p style="margin: 5px 0;"><strong>Пароль:</strong> <code style="background-color: #eee; padding: 2px 5px;">{password}</code></p>
      </div>
      
      <p style="color: #666; font-size: 13px; margin-top: 20px;">
        Вы можете изменить пароль в личном кабинете после первого входа.
      </p>
      
      <p style="color: #999; font-size: 12px; margin-top: 30px; text-align: center;">
        С уважением,<br>
        Администратор InfoCenter
      </p>
    </div>
  </body>
</html>
"""
            
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")
            message.attach(part1)
            message.attach(part2)
            
            # Отправляем письмо
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, to_email, message.as_string())
            
            logger.info(f"Password email sent successfully to {to_email}")
            return True
        
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error when sending password email to {to_email}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending password email to {to_email}: {e}")
            return False
