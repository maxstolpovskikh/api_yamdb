from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Разрешение для проверки, является ли пользователь админом."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class ReadOnly(permissions.BasePermission):
    """Разрешение для предоставления доступа только к безопасным методам."""

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsAuthorOrAdminOrModerOrReadOnly(permissions.BasePermission):
    """Разрешение для автора, админа, модератора (изменение) или для чтения."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            obj.author == request.user
            or request.user.is_admin
            or request.user.is_moderator
        )
