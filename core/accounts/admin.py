from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import User


class UserCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes password confirmation.
    """
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ("email", "username", "phone", "name")

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        username = cleaned.get("username")
        phone = cleaned.get("phone")

        if not (email or username or phone):
            raise forms.ValidationError("Provide at least one of email, username or phone.")

        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 or p2:
            if p1 != p2:
                raise forms.ValidationError("Passwords don't match.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """
    A form for updating users. Displays hashed password.
    """
    password = ReadOnlyPasswordHashField(label="Password")

    class Meta:
        model = User
        fields = ("email", "username", "phone", "name", "password", "is_active", "is_staff", "is_superuser")

    def clean_password(self):
        # return initial value
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ("__str__", "email", "username", "phone", "is_email_verified", "is_phone_verified", "is_staff", "is_superuser", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("email", "username", "phone", "name")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "username", "phone", "name", "password")}),
        ("Verification", {"fields": ("is_email_verified", "email_verified_at", "is_phone_verified", "phone_verified_at")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "phone", "name", "password1", "password2", "is_staff", "is_superuser"),
        }),
    )
    readonly_fields = ("email_verified_at", "phone_verified_at", "last_login", "date_joined")

admin.site.register(User, UserAdmin)
