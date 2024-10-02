
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer
from .models import User
import jwt, datetime
import random
from django.utils.cache import caches
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils.timezone import now  # use timezone-aware time in Django
from datetime import timedelta
from django.conf import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import urllib.parse
import urllib.request
import json

from rest_framework import status

OTP_CACHE_TIMEOUT = 300  # 5 minutes
otp_cache = caches['default']  # Use Django's default cache system (could be Redis)


class Register_View(APIView):
    permission_classes = [AllowAny]  # Allow any user to register

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            otp = random.randint(1000, 9999)  # Generate 4-digit OTP
            print(otp)  # for checking purposes
            otp_created_at = now()  # Current timestamp
            serializer.save(otp=otp, otp_created_at=otp_created_at)
            email = serializer.validated_data.get('email')

            # Email sending mechanism
            email_response = self.sendOTP(email, otp)
            print(email_response)

            if email_response['status'] == "success":
                return Response({
                    "message": "User registered successfully. OTP sent.",
                    "otp": otp  # Optionally return OTP for testing purposes
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "message": "User registered, but failed to send OTP.",
                    "error": email_response['error']
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def sendOTP(self, email, otp):
         # Email subject and body
        subject = "Your OTP Code"
        body = f"Your One-Time Password (OTP) for registration is: {otp}"

        # Create the email message
        message = MIMEMultipart()
        message["From"] = settings.EMAIL_HOST_USER
        message["To"] = email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        try:
            # Connect to Gmail SMTP server
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            server.starttls()  # Secure the connection
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)  # Login

            # Send the email
            server.sendmail(settings.EMAIL_HOST_USER, email, message.as_string())

            # Close the server
            server.quit()

            return {"status": "success", "otp": otp, "message": f"OTP sent to {email}"}

        except Exception as e:
            return {"status": "failure", "error": str(e)}


class VerifyOTP_View(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        otp_from_frontend = request.data.get('otp')  # Frontend sends the OTP
        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': f"User with email {email} doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

        # Check if OTP is valid
        if user.otp != int(otp_from_frontend):
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

        # Define OTP expiration duration (2 minutes in this case)
        otp_expiry_duration = timedelta(minutes=2)

        # Check if the OTP has expired
        if now() > user.otp_created_at + otp_expiry_duration:
            return Response({'error': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)

        # OTP is valid, activate the user
        user.is_active = True
        user.otp = None  # Clear OTP after successful verification
        user.otp_created_at = None
        user.save()

        return Response({'message': 'Account verified successfully'}, status=status.HTTP_200_OK)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Create response object
            response = Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
        
            # Set JWT tokens in cookies
            response.set_cookie(
                key='refresh_token', 
                value=str(refresh), 
                httponly=True, 
                secure=True,    # Set to True in production (use HTTPS)
                samesite='Lax'  # Helps with CSRF protection
            )
            response.set_cookie(
                key='access_token', 
                value=access_token, 
                httponly=True, 
                secure=True,    # Set to True in production (use HTTPS)
                samesite='Lax'  # Helps with CSRF protection
            )

            return response
        
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            token = token.split(' ')[1]  # Assuming the token is in "Bearer <token>" format
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired!')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token!')
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found!')

        serializer = UserSerializer(user)
        return Response(serializer.data)












'''
from django.shortcuts import render

# Create your views here.
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer
from .models import User
import jwt, datetime
import random
from django.utils.cache import caches
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils.timezone import now  # use timezone-aware time in Django
from datetime import timedelta

from rest_framework import status

OTP_CACHE_TIMEOUT = 300  # 5 minutes
otp_cache = caches['default']  # Use Django's default cache system (could be Redis)


class Register_View(APIView):
    permission_classes = [AllowAny]         # setting permission classes to allow all user for registration
    def post(self, request):
        user_email = request.data.get('email')
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            otp = random.randint(1000, 9999)  # Generate 4-digit OTP
            print(otp)   # for checking
            otp_created_at = now()  # Current timestamp
            serializer.save(otp=otp, otp_created_at=otp_created_at)

            # email sending mechanism
            google_script_url = 'https://script.google.com/macros/s/AKfycbw6mr1rXgjdzNsYB0zQnWrjuFKro6u8HNsX58v7hEZT87c2RBTZyiMFZrPWZGGzop_wOQ/exec'

            # Make a request to Google Apps Script
            try:
                response = requests.post(google_script_url, json={
                    'recipient': user_email,
                    'otp': otp
                })
            except Exception as e:
                return Response({'error': "otp can't be sent"}, status=status.HTTP_502_BAD_GATEWAY)
            
            return Response({'error': "otp sent"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class VerifyOTP_View(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        otp_from_frontend = request.data.get('otp')        # think about hashing password, otp before sending over api
        email = request.data.get('email')

        try:
            user  = User.objects.get(email = email)
        except User.DoesNotExist:
            return Response({'error': "User having {email}, doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if OTP is valid
        if user.otp != int(otp_from_frontend):
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Define OTP expiration duration (2 minutes in this case)
        otp_expiry_duration = timedelta(minutes=2)

        # Check if the OTP has expired
        if now() > user.otp_created_at + otp_expiry_duration:
            return Response({'error': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)
        
        # OTP is valid, activate the user
        user.is_active = True
        user.otp = None  # Clear OTP after successful verification
        user.otp_created_at = None
        user.save()

        return Response({'message': 'Account verified successfully'}, status=status.HTTP_200_OK)

    
class LoginView(APIView):
    permission_classes = [AllowAny]         # setting permission classes to allow all user for login
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            response_data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            
class UserView(APIView):
    def get(self, request):
        token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            token = token.split(' ')[1]  # Assuming the token is in "Bearer <token>" format
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired!')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token!')
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found!')
        
        serializer = UserSerializer(user)
        return Response(serializer.data)
'''
