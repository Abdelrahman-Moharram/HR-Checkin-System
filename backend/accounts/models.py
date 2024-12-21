from django.db import models
from hr.models import Office
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin
)


class UserAccountManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        email = email.lower()

        user = self.model(
            email=email,
            **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **kwargs):
        user = self.create_user(
            email,
            password=password,
            **kwargs
        )
        role = Role.objects.filter(name='Admin').first()
        if not role:
            role = Role.objects.create(name='Admin')
            role.save()
        user.role  = role
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user

class Role(models.Model):
    name                = models.CharField(max_length=255)
    def __str__(self) -> str:
        return self.name



class User(AbstractBaseUser, PermissionsMixin):
    name                = models.CharField(max_length=255)
    email               = models.EmailField(unique=True, max_length=255)
    is_active           = models.BooleanField(default=True)
    role                = models.ForeignKey(Role, on_delete=models.CASCADE)
    office              = models.ForeignKey(Office, related_name='office_users', null=True, blank=True, on_delete=models.SET_NULL)
    is_staff            = models.BooleanField(default=False)
    is_superuser        = models.BooleanField(default=False)
    
    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name',]

    def __str__(self):
        return self.email
    

    def save(self, *args, **kwargs):
        # Save the provided password in hashed format
        user = super(User, self)
        if not (user.is_superuser):
            user.set_password(self.password)
        super().save(*args, **kwargs)
        return user
    


