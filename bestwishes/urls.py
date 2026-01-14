from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path("admin/", admin.site.urls),
    path('users/', include('users.urls')),
    path('wishlists/', include('wishlists.urls')),
    path('gifts/', include('gifts.urls')),
]
