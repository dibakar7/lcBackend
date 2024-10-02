
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self,name, email, password=None, **extra_fields):
        if not name:
            raise ValueError("User must have an name")
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, email, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(name, email, password, **extra_fields)


class User(AbstractBaseUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)

    otp = models.IntegerField(null=True, blank=True)           # this is for future use. if decided that otp must be stored inside DB
    otp_created_at = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=False)  # set to false until otp verification is done
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # Remove the username field, as it's not used
    username = None

    USERNAME_FIELD = 'email'  # Set email as the unique identifier for login
    REQUIRED_FIELDS = ['name', 'password']  # No required fields other than email and password

    objects = CustomUserManager()  # Set the custom manager

    def __str__(self):
        return self.email

    

    

'''{
"name":"a",
"email":"a@a.com",
"password":"a"
}'''
