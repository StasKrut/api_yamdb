from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """ Проверка на зарегестрированного пользователя - себя
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_staff
            or request.user.role == request.user.ADMIN
            or obj.username == request.user
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """ Проверка на админа или только для чтения
    """
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.role == request.user.ADMIN
        )


class IsAuthorOrReadOnly(permissions.BasePermission):
    """ Проверка на автора для изменения,
    зарегестрированного пользователя для создания или только для чтения
    """
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_staff
            or request.user.role == request.user.ADMIN
        )
