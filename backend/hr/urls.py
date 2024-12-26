from django.urls import path
from .views import *

app_name = 'hr'

urlpatterns = [
    path('offices/', offices_list, name='offices_list'),
    path('offices/<int:office_id>/', get_office, name='get_office'),
    path('offices/<int:office_id>/change-location/', change_office_location, name='change_office_location'),


    path('offices/<int:office_id>/employees/add/', add_user_to_office, name='add_user_to_office'),
    path('offices/<int:office_id>/employees/check-in/', check_in, name='check_in'),
    path('offices/<int:office_id>/employees/check-out/', check_out, name='check_out'),
    path('offices/<int:office_id>/employees/check-ins/', get_check_ins_history, name='get_check_ins_history'),
    path('offices/<int:office_id>/employees/total-attendance-hours/', calculate_daily_total_hours, name='calculate_daily_total_hours'),
    
    path('offices/<int:office_id>/employees/<int:employee_id>/check-ins/', get_check_ins_history_for_employee, name='get_check_ins_history_for_employee'),
    path('offices/<int:office_id>/employees/<int:employee_id>/status/', get_employee_status, name='get_employee_status'),
]
