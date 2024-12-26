from django.shortcuts import render


def index(request):
    return render(request, "communications/index.html")
    
def room(request, room_name):
    return render(request, "communications/room.html", {"room_name": room_name})    