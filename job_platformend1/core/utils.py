# utils.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import EmailVerificationCode

def send_verification_email(user, email, purpose):
    # Удаляем старые коды для этого пользователя и цели
    EmailVerificationCode.objects.filter(user=user, purpose=purpose).delete()
    
    # Создаем новый код
    code = EmailVerificationCode.objects.create(
        user=user,
        email=email,
        purpose=purpose
    )
    
    # Формируем сообщение
    subject = "Код подтверждения"
    if purpose == 'email_binding':
        subject = "Подтверждение привязки email"
    elif purpose == 'password_reset':
        subject = "Сброс пароля"
    
    html_message = render_to_string('email/verification_code.html', {
        'code': code.code,
        'purpose': purpose,
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        None,  # Используется DEFAULT_FROM_EMAIL
        [email],
        html_message=html_message,
    )