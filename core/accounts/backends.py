from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

UserModel = get_user_model()


class MultiFieldModelBackend(ModelBackend):
    """
    Authenticate using email OR username OR phone.
    The "username" parameter passed to authenticate() is treated as the identifier.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            # Django sometimes passes kwargs like email=... so check there
            username = kwargs.get(UserModel.USERNAME_FIELD) or kwargs.get("email") or kwargs.get("phone")

        if username is None:
            return None

        try:
            user = UserModel.objects.get(
                Q(email__iexact=username) | Q(username__iexact=username) | Q(phone__iexact=username)
            )
        except UserModel.DoesNotExist:
            return None

        # use check_password from AbstractBaseUser
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None