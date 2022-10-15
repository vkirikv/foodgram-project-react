from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        """
        Разрешение на достук к объекту владельцу обЪекта.
        """
        return request.method in SAFE_METHODS or obj.author == request.user
