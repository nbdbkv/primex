from rest_framework import permissions
from base64 import b64decode
from account.models import User


class IsAuth(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            auth = request["Authorization"].split(" ")[1]
            username, password = b64decode(auth).decode("utf-8").split(":")
            user = User.objects.get(phone=username, password=password)
            return True
        except:
            return False
