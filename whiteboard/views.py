from django.shortcuts import render

def home(request):
    whiteboard = {
        "Room 1": {"provider": "Dr. Smith", "surgeon": "Dr. Jones"},
        "Room 2": {"provider": "Dr. Lee", "surgeon": "Dr. Patel"}
    }
    return render(request, 'index.html', {'whiteboard': whiteboard})