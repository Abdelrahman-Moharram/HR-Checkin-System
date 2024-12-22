from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Office, Office_Location, Attendance
from .permissions import IsOfficeAdmin, IsOfficeMember
from .serializer import *
from rest_framework.decorators import api_view, permission_classes
from accounts.serializers import UserFormSerial
from project.helper import haversine, to_float_or_0
from datetime import datetime, timezone
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