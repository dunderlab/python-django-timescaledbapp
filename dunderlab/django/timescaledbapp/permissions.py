from rest_framework import permissions


class AdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        group_name = "api_admin"
        return request.user.groups.filter(name=group_name).exists()


class ConsumerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        group_name = "api_consumer"
        return request.user.groups.filter(name=group_name).exists()


class ProduserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        group_name = "api_produser"
        return request.user.groups.filter(name=group_name).exists()
