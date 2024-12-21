from django.urls import path
from .views import *

app_name = 'hr'

urlpatterns = [
    path('offices/', offices_list, name='offices_list'),
    path('offices/<str:office_id>/', get_office, name='get_office'),
    path('offices/<str:office_id>/employees/add/', add_user_to_office, name='add_user_to_office'),
]
