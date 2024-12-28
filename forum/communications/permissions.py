from rest_framework.permissions import BasePermission
from .models import Room


class IsParticipant(BasePermission):
    def has_permission(self, request, view):
        room_id = view.kwargs.get("conversation_id")
        room = Room.objects.filter(pk=room_id).first()
        return room and request.user in room.online.all()
