from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class NoPasswordAuthBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        UserModel = get_user_model()

        try:
            user = UserModel._default_manager.get(email=email)
        except UserModel.DoesNotExist:
            return None

        return user if user else None