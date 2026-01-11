from django.urls import path
from django.http import HttpResponse

def health(request):
    return HttpResponse("users ok")

urlpatterns = [
    path("", health),
]
