from django.contrib.auth import models
from rest_framework import permissions


class IsAdminOrEditOnly(permissions.BasePermission):
    ALLOW_METHODS = ('GET', 'PUT', 'OPTIONS', 'HEAD')

    def has_object_permission(self, request, view, obj):
        if request.method in self.ALLOW_METHODS:
            return True
        return request.user.is_staff

