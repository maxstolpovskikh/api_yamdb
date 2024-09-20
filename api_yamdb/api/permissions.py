from rest_framework.permissions import IsAuthenticated


class IsAuthenticatedAdmin(IsAuthenticated):

    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        return is_authenticated and (
            request.user.role == 'admin' or request.user.is_superuser
        )
