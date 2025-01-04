from rest_framework.permissions import BasePermission
from .models import Room
from bson import ObjectId


class IsParticipant(BasePermission):
    def has_permission(self, request, view):
        room_id = view.kwargs.get("room_id")

        try:
            room_object_id = ObjectId(room_id)
        except Exception:
            return False

        room = Room.objects.filter(id=room_object_id).first()

        if room and request.user.user_id in room.participants:
            return True

        return False
