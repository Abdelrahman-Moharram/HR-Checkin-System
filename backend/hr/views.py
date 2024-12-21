from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Office
from .permissions import IsOfficeAdmin
from .serializer import *
from rest_framework.decorators import api_view, permission_classes
from accounts.serializers import UserFormSerial

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




def check_in(request):
    long = request.POST['longitude']
    lat = request.POST['latitude']