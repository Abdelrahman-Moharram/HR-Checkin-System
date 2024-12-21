from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import User, Role
import re
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['id'] = str(user.id)
        token['email'] = user.email
        token['name'] = user.name
        if user.role:
            token['role'] = user.role.name
        

        return token


class BaseUserSerial(serializers.ModelSerializer):
    class Meta:
        model= User
        fields=['id', 'email', 'name']

class UserSerial(serializers.ModelSerializer):
    role   = serializers.SerializerMethodField()
    def get_role(self, obj):
        if obj.role:
            return obj.role.name
        return None
    class Meta:
        model= User
        fields=['id', 'email', 'name', 'role']

class UserFormSerial(serializers.ModelSerializer):
    
    class Meta:
        model= User
        fields=['email', 'name', 'role', 'password']


    @property
    def is_update(self):
        return self.instance is not None
    
         
    
    def validate_email(self, value):
        value = value.strip()

        if not re.fullmatch('^[a-z][a-z0-9-_\\.]+@[a-z.]+\\.[a-z]{2,3}$', value):
            raise serializers.ValidationError('This Email Address is Invalid')

        if not self.is_update and User.objects.filter(email=value).exists():
            raise serializers.ValidationError('This Email already exists with another Employee')
        return value
    

    def save(self, **kwargs):
        if not self.is_update:
            self.office = kwargs['office']
        
        return super().save(**kwargs)