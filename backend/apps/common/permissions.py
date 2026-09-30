from rest_framework.permissions import BasePermission


class HasRole(BasePermission):
    allowed_roles: tuple[str, ...] = ()

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role in self.allowed_roles)


class IsStudentUser(HasRole):
    allowed_roles = ("STUDENT",)


class IsMonitorUser(HasRole):
    allowed_roles = ("MONITOR",)


class IsAdminUser(HasRole):
    allowed_roles = ("ADMIN",)
