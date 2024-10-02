
from django.urls import path, include
from .views import Register_View, LoginView, UserView, VerifyOTP_View
urlpatterns = [
   
    path('register/', Register_View.as_view()),
    path('login/', LoginView.as_view()),
    path('user/', UserView.as_view()),
    path('verify-otp/', VerifyOTP_View.as_view()),
    
]
