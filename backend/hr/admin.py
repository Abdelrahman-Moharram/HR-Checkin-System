from django.contrib import admin
from .models import Location, Office, Office_Location, Attendance

admin.site.register(Location)
admin.site.register(Office)
admin.site.register(Office_Location)
admin.site.register(Attendance)
