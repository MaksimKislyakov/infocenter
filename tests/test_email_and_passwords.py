import os
os.environ["TESTING"] = "true"

import pytest
from app.services.auth_service import generate_password, verify_password, get_password_hash
from app.services.email.email_service import EmailService
import string


class TestPasswordGeneration:
    """Тесты для функции генерирования паролей"""
    
    def test_password_generation_default_length(self):
        """Проверяет что сгенерированный пароль имеет корректную длину"""
        password = generate_password()
        assert len(password) == 12
    
    def test_password_generation_custom_length(self):
        """Проверяет что можно сгенерировать пароль нужной длины"""
        password = generate_password(length=16)
        assert len(password) == 16
    
    def test_password_has_lowercase(self):
        """Проверяет что пароль содержит хотя бы одну строчную букву"""
        password = generate_password()
        assert any(c in string.ascii_lowercase for c in password)
    
    def test_password_has_uppercase(self):
        """Проверяет что пароль содержит хотя бы одну заглавную букву"""
        password = generate_password()
        assert any(c in string.ascii_uppercase for c in password)
    
    def test_password_has_digit(self):
        """Проверяет что пароль содержит хотя бы одну цифру"""
        password = generate_password()
        assert any(c in string.digits for c in password)
    
    def test_password_has_special_char(self):
        """Проверяет что пароль содержит хотя бы один спецсимвол"""
        password = generate_password()
        assert any(c in "!@#$%^&*" for c in password)
    
    def test_password_uniqueness(self):
        """Проверяет что каждое сгенерированное значение уникально"""
        passwords = {generate_password() for _ in range(100)}
        assert len(passwords) == 100, "Должны быть разные пароли"
    
    def test_password_can_be_hashed_and_verified(self):
        """Проверяет что сгенерированный пароль корректно хешируется и проверяется"""
        password = generate_password()
        password_hash = get_password_hash(password)
        assert verify_password(password, password_hash)
        assert not verify_password("wrong_password", password_hash)


class TestEmailService:
    """Тесты для EmailService"""
    
    def test_email_service_initialization(self):
        """Проверяет что EmailService инициализируется без ошибок"""
        service = EmailService()
        assert service is not None
        assert service.smtp_server == "smtp.mail.ru"
        assert service.smtp_port == 465
    
    def test_send_password_email_no_credentials(self):
        """Проверяет что отправка письма корректно обрабатывает отсутствие credentials"""
        service = EmailService()
        # Удаляем credentials
        service.sender_email = ""
        service.sender_password = ""
        
        result = service.send_password_email("test@example.com", "testuser", "password123")
        # Должна вернуть False если нет credentials
        assert result is False
