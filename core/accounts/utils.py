from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta

User = get_user_model()
token_generator = PasswordResetTokenGenerator()


def make_uid(user):
    return urlsafe_base64_encode(force_bytes(user.pk))


def make_token(user):
    return token_generator.make_token(user)

def send_verification_email(user, request=None, purpose='verify'):
    code = get_random_string(length=5, allowed_chars='0123456789')
    user.email_verification_code = code
    user.email_verification_expiry = timezone.now() + timedelta(minutes=10)
    user.save(update_fields=['email_verification_code','email_verification_expiry'])

    subject = "Verify your email"
    message = f"Your verification code is: {code}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

def send_sms_stub(phone, text):
    # Replace with Twilio or other provider
    # For now just print/log (or integrate real sender)
    print(f"SMS to {phone}: {text}")

def send_verification_via_sms(user, purpose='verify'):
    # تولید کد ۵ رقمی تصادفی
    code = get_random_string(length=5, allowed_chars='0123456789')
    user.phone_verification_code = code
    user.phone_verification_expiry = timezone.now() + timedelta(minutes=10)
    user.save(update_fields=['phone_verification_code', 'phone_verification_expiry'])

    text = f"Your verification code is: {code}"
    send_sms_stub(user.phone, text)