from rest_framework import permissions


class IsAdminOrSuperUser(permissions.BasePermission):
    """
    Проверка прав доступа.
    Проверяет, является ли пользователь админом.
    """
    def has_permission(self, request, view):
        # просто проверяет, авторизован ли пользователь
        # если нет, то не дает ничего делать
        if not request.user.is_authenticated:
            return False
        # а админам и суперпользователям разрешено
        if request.user.is_admin or request.user.is_superuser:
            return True
        return False


class IsAuthorOrAdminOrModeratorOrReadOnly(permissions.BasePermission):
    """
    Права доступа: чтение для всех
    изменение только для автора, админа и модератора.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if obj.author == request.user:
            return True
        # а админам и модераторам разрешено
        if request.user.is_admin or request.user.is_moderator:
            return True
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Права доступа: чтение для всех
    изменение только для админа и суперпользователя.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            # а админам и суперпользователям разрешено
            if request.user.is_admin or request.user.is_superuser:
                return True
        return False
