from rest_framework import serializers
from .models import Office, Location, Attendance
from accounts.serializers import UserSerial

class ViewLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        # fields = '__all__'
        exclude = ['id', ]

class OfficListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
    
    def to_representation(self, instance):
        location_serial = ViewLocationSerializer(data=[instance.location], many=True)
        if not location_serial.is_valid():
            pass

        rep = dict()
        
        rep['id']           = instance.id
        rep['name']         = instance.name
        rep['location']     = location_serial.data[0] if location_serial.data else ''


        return rep
    
class OfficeDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
    
    def to_representation(self, instance):
        locations_serial = ViewLocationSerializer(data=instance.locations, many=True)
        users_serial     = UserSerial(data=instance.office_users, many=True)
        if not locations_serial.is_valid():
            pass
        if not users_serial.is_valid():
            pass
        rep = dict()
        
        rep['id']           = instance.id
        rep['name']         = instance.name
        rep['locations']    = locations_serial.data
        rep['employees']     = users_serial.data
        return rep


class AttendanceSerializer(serializers.ModelSerializer):
    is_active   = serializers.SerializerMethodField()
    def get_is_active(self, obj):
        if not obj.check_out:
            return True
        return False
    class Meta:
        model = Attendance
        fields = [
            'check_in',
            'check_out',
            'is_active'
        ]

class EmployeeAttendanceSerializer(serializers.ModelSerializer):
    is_active   = serializers.SerializerMethodField()
    user        = serializers.SerializerMethodField()
    def get_is_active(self, obj):
        if not obj.check_out:
            return True
        return False
    
    def get_user(self, obj):
        return obj.user.name
    
    class Meta:
        model = Attendance
        fields = [
            'check_in',
            'check_out',
            'is_active',
            'user'
        ]