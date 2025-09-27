from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q
import uuid

class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, name, email,username,phone, password, **extra_fields):
        if not (email or username or phone):
            raise ValueError("A user must have at least one of: email, username or phone.")
        
        email = self.normalize_email(email) if email else None
        
        user = self.model(
            email=email,
            name=name,
            username=username,
            phone=phone,
            **extra_fields
        )
        
        if password:
            user.set_password(password)
        else:
            # set unusable password if not provided
            user.set_unusable_password()
        user.save(using=self._db)

        return user

    def create_user(self, name=None,username=None, phone=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email=email, username=username, phone=phone, name=name, password=password, **extra_fields)    
    
    def create_superuser(self, email=None, username=None, phone=None, name=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        # require at least one identifier for superuser too
        if not (email or username or phone):
            raise ValueError("Superuser must have at least one of: email, username or phone.")

        return self._create_user(email=email, username=username, phone=phone, name=name, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    
    # identifiers are optional but unique
    email = models.EmailField(max_length=255, unique=True, blank=True, null=True)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    phone = models.CharField(max_length=30, unique=True, blank=True, null=True)
            
    # phone verification
    phone_verification_code = models.CharField(max_length=6, blank=True, null=True)
    phone_verification_expiry = models.DateTimeField(blank=True, null=True)
    
    is_phone_verified = models.BooleanField(default=False)
    phone_verified_at = models.DateTimeField(blank=True, null=True)

    # Email verification
    email_verification_code = models.CharField(max_length=32, blank=True, null=True)
    email_verification_expiry = models.DateTimeField(blank=True, null=True)
    # verification flags + timestamps
    is_email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def clean(self):
        # Ensure at least one identifier is present
        if not (self.email or self.username or self.phone):
            raise ValidationError("User must have at least one of email, username, or phone.")

    def get_short_name(self):
        return self.name or (self.username or self.email or self.phone)

    def get_full_name(self):
        return self.name or self.get_short_name()

    def __str__(self):
        # show the best available identifier
        return self.email or self.username or self.phone or str(self.id)

    def verify_email(self, save=True):
        """Mark email verified (idempotent)."""
        if not self.is_email_verified:
            self.is_email_verified = True
            self.email_verified_at = timezone.now()
            if save:
                self.save(update_fields=["is_email_verified", "email_verified_at"])

    def verify_phone(self, save=True):
        """Mark phone verified (idempotent)."""
        if not self.is_phone_verified:
            self.is_phone_verified = True
            self.phone_verified_at = timezone.now()
            if save:
                self.save(update_fields=["is_phone_verified", "phone_verified_at"])

    def unverify_email(self, save=True):
        """Optional: rollback email verification."""
        if self.is_email_verified:
            self.is_email_verified = False
            self.email_verified_at = None
            if save:
                self.save(update_fields=["is_email_verified", "email_verified_at"])

    def unverify_phone(self, save=True):
        """Optional: rollback phone verification."""
        if self.is_phone_verified:
            self.is_phone_verified = False
            self.phone_verified_at = None
            if save:
                self.save(update_fields=["is_phone_verified", "phone_verified_at"])
    def generate_email_verification_code(self):
        self.email_verification_code = get_random_string(length=5)
        self.email_verification_expiry = timezone.now() + timedelta(hours=24)
        self.save(update_fields=["email_verification_code", "email_verification_expiry"])
        return self.email_verification_code

    def generate_phone_verification_code(self):
        self.phone_verification_code = get_random_string(length=5, allowed_chars='0123456789')
        self.phone_verification_expiry = timezone.now() + timedelta(minutes=10)
        self.save(update_fields=["phone_verification_code", "phone_verification_expiry"])
        return self.phone_verification_code

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        # You can add indexes for lookups on email/username/phone
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["username"]),
            models.Index(fields=["phone"]),
        ]
    