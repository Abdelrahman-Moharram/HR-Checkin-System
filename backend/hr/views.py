from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Office, Office_Location, Attendance
from .permissions import IsOfficeAdmin, IsOfficeMember
from .serializer import *
from rest_framework.decorators import api_view, permission_classes
from accounts.serializers import UserFormSerial
from project.helper import haversine, to_float_or_0, export_as_excel
from datetime import datetime, timezone, date
from accounts.models import User



def get_office_or_return_404(id):
    office = Office.objects.filter(id=id)
    if not office:
        res = Response(
                {
                    'error': "this office doesn't exist or maybe deleted"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        return {'is_valid':False, 'office': None, 'response':res}
    return {'is_valid':True, 'office': office, 'response':None}


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def offices_list(request):
        
    offices_serial = OfficListSerializer(data=Office.objects.all(), many=True)

    if not offices_serial.is_valid():
        pass

    return Response(
            {
                'offices': offices_serial.data
            },
            status=status.HTTP_200_OK
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_office(request, office_id):
    
    check_office = get_office_or_return_404(office_id)
    if not check_office['is_valid']:
        return check_office['response']
    
    office = check_office['office']
    office_serial = OfficeDetailsSerializer(data=office, many=True)

    if not office_serial.is_valid():
        pass

    return Response(
            {
                'offices': office_serial.data[0]
            },
            status=status.HTTP_200_OK
        )

@api_view(['POST'])
@permission_classes([IsOfficeAdmin])
def add_user_to_office(request, office_id):

    check_office = get_office_or_return_404(office_id)
    if not check_office['is_valid']:
        return check_office['response']
    
    office = check_office['office']

    form = UserFormSerial(data=request.POST)

    if form.is_valid():
        form.save(office=office.first())

        return Response(
            {'message':f'Employee "{request.POST['name']}" added Successfully'},
            status=status.HTTP_201_CREATED
        )
    return Response(
            {'errors':form.errors},
            status=status.HTTP_400_BAD_REQUEST
        )






@api_view(['POST'])
@permission_classes([IsOfficeMember])
def check_in(request, office_id):
    latitude    = request.POST.get('latitude', None)
    longitude   = request.POST.get('longitude', None)

    if not latitude or not longitude:
        return Response(
            {
                'message': "Invalid location, Can't get your coordinates correctly try again later"
            },
            status=status.HTTP_400_BAD_REQUEST
        ) 

    


    o_location = Office_Location.objects.filter(office__id=office_id)
    if not o_location:
        return Response(
            {
                'error': f'This office is not found or has been deleted'
            },
            status=status.HTTP_404_NOT_FOUND
        )
    

    o_location = o_location.filter(is_present=True).first()
    if not o_location:
        return Response(
            {
                'error': "can't check in because this office currently has no location"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    location = o_location.location
        

    is_valid_distance = haversine(lat1=to_float_or_0(latitude), lon1=to_float_or_0(longitude), lat2=location.latitude, lon2=location.longitude, office_radius=5)

    if is_valid_distance:
        attendance = Attendance.objects.filter(office=o_location.office, user=request.user, check_out=None).first()
        if attendance:
            return Response(
                {
                    'message': f'Welcome {request.user.name}, You are already checked in recently at {attendance.check_in}'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        attendance = Attendance.objects.create(office=o_location.office, user=request.user)
        attendance.save()

        return Response(
            {
                'message': f'Welcome {request.user.name}, you are checked in successfully'
            },
            status=status.HTTP_201_CREATED
        )
    return Response(
        {
            'message': 'Invalid Location, you should check in from closer area please try again when you are closer'
        },
        status=status.HTTP_400_BAD_REQUEST
    )



@api_view(['POST'])
@permission_classes([IsOfficeMember])
def check_out(request, office_id):
    latitude    = request.POST.get('latitude', None)
    longitude   = request.POST.get('longitude', None)

    if not latitude or not longitude:
        return Response(
            {
                'message': "Invalid location, Can't get your coordinates correctly try again later"
            },
            status=status.HTTP_400_BAD_REQUEST
        ) 

    


    o_location = Office_Location.objects.filter(office__id=office_id)
    if not o_location:
        return Response(
            {
                'error': f'This office is not found or has been deleted'
            },
            status=status.HTTP_404_NOT_FOUND
        )
    

    o_location = o_location.filter(is_present=True).first()
    

    location = o_location.location
        

    is_valid_distance = haversine(lat1=to_float_or_0(latitude), lon1=to_float_or_0(longitude), lat2=location.latitude, lon2=location.longitude, office_radius=5)

    if is_valid_distance:
        attendance = Attendance.objects.filter(office=o_location.office, user=request.user, check_out=None).first()
        if attendance:
            attendance.check_out = datetime.now(tz=timezone.utc)
            attendance.save()
            return Response(
                {
                    'message': f'You are checked out successfully at {attendance.check_out}'
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                'message': f'You have no active check in, you already checked out'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    return Response(
        {
            'message': 'Invalid Location, you should check out from closer area please try again when you are closer'
        },
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['GET'])
@permission_classes([IsOfficeAdmin])
def get_check_ins_history(request, office_id):
    attendances             = Attendance.objects.filter(office__id=office_id).order_by('-check_in')
    attendances_serial      = EmployeeAttendanceSerializer(data=attendances, many=True)

    if not attendances_serial.is_valid():
        pass

    if 'excel' in request.GET:
        return export_as_excel(data=attendances_serial.data, file_name='Attendances', excluded_cols=[])
    return Response(
        {
            'attendances': attendances_serial.data,
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([IsOfficeAdmin])
def get_check_ins_history_for_employee(request, office_id, employee_id):
    
    employee        = User.objects.filter(id=employee_id).first()
    if not employee:
        return Response(
            {
                'error': 'This Employee is Not Found or has been deleted'
            },
            status=status.HTTP_404_NOT_FOUND
        )
    attendances             = Attendance.objects.filter(office__id=office_id, user=employee).order_by('-check_in')
    attendances_serial      = AttendanceSerializer(data=attendances, many=True)


    if not attendances_serial.is_valid():
        pass

    

    return Response(
        {
            'employee_name': employee.name,
            'attendances': attendances_serial.data,
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([IsOfficeAdmin])
def get_employee_status(request, office_id, employee_id):
    
    attendance = Attendance.objects.filter(office__id=office_id, user__id=employee_id)
    if not attendance:
        return Response(
            {
                'error': "this employee isn't registered in this office"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    today = datetime.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())
    return Response(
        {
            'status': 'present' if attendance.filter(check_in__range=(start_of_day, end_of_day)).exists() else 'absent',
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([IsOfficeAdmin])
def change_office_location(request, office_id):
    check_office = get_office_or_return_404(office_id)
    if not check_office['is_valid']:
        return check_office['response']
    
    office = check_office['office'].first()

    latitude        = request.POST.get('latitude', None)
    longitude       = request.POST.get('longitude', None)
    office_radius   = request.POST.get('office_radius', None)


    if not latitude or not longitude or not office_radius:
        return Response(
            {
                'message': "Invalid location, Can't get your coordinates correctly try again later"
            },
            status=status.HTTP_400_BAD_REQUEST
        ) 

    # TODO -> take the result of this function instead of checking the exact location of lat, long existance because it might not the same actual value
    # haversine(lat1=to_float_or_0(office.location.latitude), lon1=to_float_or_0(office.location.longitude), lat2=location.latitude, lon2=location.longitude, office_radius=office_radius)
    location, is_created = Location.objects.get_or_create(longitude=longitude, latitude=latitude)

    if not is_created:
        o_location      = Office_Location.objects.filter(office=office, location=location).first()
        if not o_location.is_present:

            # checkout all checkedin employees
            Attendance.objects.filter(office=office, check_out=None).update(check_out=datetime.now(tz=timezone.utc))
            # change Location state to be not present
            Office_Location.objects.filter(office=office, is_present=True).update(is_present=False)
            
            o_location.is_present   = True
            o_location.save()
            return Response(
                {
                    'message': f'Office {office.name} Location is Switched to old Location successfully!'
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                'error': f'The old Office Location is the same of the new location'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    else:

        # checkout all checkedin employees
        Attendance.objects.filter(office=office, check_out=None).update(check_out=datetime.now(tz=timezone.utc))
        # change Location state to be not present
        Office_Location.objects.filter(office=office, is_present=True).update(is_present=False)

        # Creating new location
        o_location      = Office_Location.objects.create(office=office, location=location, is_present=True)
        o_location.save()


        

        return Response(
            {
                'message': f'Office {office.name} Location is changed successfully!'
            },
            status=status.HTTP_201_CREATED
        )



@api_view(['GET'])
@permission_classes([IsOfficeAdmin])
def calculate_daily_total_hours(request, office_id):
    today = datetime.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())
    attendanecs = Attendance.objects.filter(office__id=office_id,check_in__range=(start_of_day, end_of_day)).order_by('-check_in')
    
    total_hours = dict()
    for attendance in attendanecs:
        check_out = attendance.check_out if attendance.check_out else datetime.now(tz=timezone.utc)
        if attendance.user.name in total_hours:
            total_hours[attendance.user.name] += check_out - attendance.check_in
        else:
            total_hours[attendance.user.name] = check_out - attendance.check_in

    for user in total_hours.keys():
        hours, remainder = divmod(total_hours[user].total_seconds(), 3600)
        minutes = remainder // 60
        total_hours[user] = f"{int(hours):02}:{int(minutes):02}"
    print(total_hours)
    return Response(
        {
            'total_hours': total_hours
        },
        status=status.HTTP_200_OK
    )