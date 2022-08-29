from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """ Проверка на автора
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
