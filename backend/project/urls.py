from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/', include('hr.urls', namespace='hr')),
    path('api/users/', include('accounts.urls', namespace='accounts')),
    path('admin/', admin.site.urls),
]
