from django.contrib.auth import backends
from django.shortcuts import get_object_or_404
from reviews.models import User


class AuthenticationWithoutPasswordBackend(backends.ModelBackend):
    """
    Дополнительный Backend для аутентификации без пароля, но
    с использованием кода подтверждения.
    """

    def authenticate(self, request, *args, **kwargs):
        return get_object_or_404(User, username=kwargs['username'])
