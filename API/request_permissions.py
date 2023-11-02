from rest_framework import permissions

class CustomPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow GET and POST requests
        if request.method in ('GET', 'POST'):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        # Deny PUT (update) and DELETE requests
        if request.method in ('PUT', 'DELETE'):
            return False
        return True