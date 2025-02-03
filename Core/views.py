from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from rest_framework import status
from .models import PasswordReset
from .serializers import RegisterSerializer, LoginSerializer, ForgotPasswordSerializer, ResetPasswordSerializer



@login_required # restrict page to authenticated users
def Home(request):
    access_token = request.GET.get('access_token', None)
    return render(request, 'index.html', {'access_token': access_token})

def RegisterView(request):
    
    if request.method == 'POST':
        # Getting user inputs from frontend
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user_data_has_error = False

        # Make sure email and username are not being used
        if User.objects.filter(username=username).exists():
            user_data_has_error = True
            messages.error(request, 'Username already exists')

        if User.objects.filter(email=email).exists():
            user_data_has_error = True
            messages.error(request, 'Email already exists')

        # Make sure password is at least 5 characters long
        if len(password) < 5:
            user_data_has_error = True
            messages.error(request, 'Password must be at least 5 characters')

        if user_data_has_error:
            return redirect('register')
        else:
            # Create the user
            new_user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password
            )
            messages.success(request, "Account created. Login now")
            return redirect('login')

    # Handle GET request (render the registration form)
    return render(request, 'register.html')




# def LoginView(request):
#     if request.method == 'POST':

#         # getting user inputs from frontend
#         username = request.POST.get('username')
#         password = request.POST.get('password')

#         # authenticate user
#         user = authenticate(request, username=username, password=password)
        
#         if user is not None:
#             # login user if login credentials are correct
#             login(request, user)

#             refresh = RefreshToken.for_user(user)
#             access_token = str(refresh.access_token)

#             # ewdirect to home page
#             return redirect(f"/?access_token={access_token}")

#         else:
#             # redirect back to the login page if credentials are wrong
#             messages.error(request, 'Invalid user credentials')
#             return redirect('login')


#     return render(request, 'sign-in.html')

class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Login user",
        request=LoginSerializer,
        responses={200: "Login successful", 401: "Invalid credentials"}
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    "message": "Login successful",
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh)
                }, status=status.HTTP_200_OK)
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def LogoutView(request):

    logout(request)

    # redirect to login page after logout
    return redirect('login')

def ForgotPassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        # Verify if email exists
        try:
            user = User.objects.get(email=email)

            # Create a new reset ID
            new_password_reset = PasswordReset(user=user)
            new_password_reset.save()

            # Create password reset URL
            password_reset_url = reverse('reset-password', kwargs={'reset_id': new_password_reset.reset_id})
            full_password_reset_url = f"{request.scheme}://{request.get_host()}{password_reset_url}"

            # Email content
            email_body = f'Reset your password using the link below:\n\n{full_password_reset_url}'

            email_message = EmailMessage(
                'Reset your password',  # Email subject
                email_body,
                settings.EMAIL_HOST_USER,  # Email sender
                [email]  # Email receiver
            )

            email_message.fail_silently = True
            email_message.send()

            return redirect('password-reset-sent', reset_id=new_password_reset.reset_id)

        except User.DoesNotExist:
            messages.error(request, f"No user with email '{email}' found")
            return redirect('forgot-password')

    return render(request, 'forgot_password1.html')

def PasswordResetSent(request, reset_id):

    # check if reset id exists
    if PasswordReset.objects.filter(reset_id=reset_id).exists():
        return render(request, 'password_reset_sent.html')
    else:
        # redirect to forgot password page if code does not exist
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')
    

def ResetPassword(request, reset_id):

    try:
        password_reset_id = PasswordReset.objects.get(reset_id=reset_id)
        if request.method == 'POST':

            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            passwords_have_error = False

            if password != confirm_password:
                passwords_have_error = True
                messages.error(request, 'Passwords do not match')

            if len(password) < 5:
                passwords_have_error = True
                messages.error(request, 'Password must be at least 5 characters long')

            # check to make sure link has not expired
            expiration_time = password_reset_id.created_when + timezone.timedelta(minutes=10)

            if timezone.now() > expiration_time:
                passwords_have_error = True
                messages.error(request, 'Reset link has expired')

                password_reset_id.delete()

            # reset password
            if not passwords_have_error:
                user = password_reset_id.user
                user.set_password(password)
                user.save()
                
                # delete reset id after use
                password_reset_id.delete()

                # redirect to login
                messages.success(request, 'Password reset. Proceed to login')
                return redirect('login')

            else:
                # redirect back to password reset page and display errors
                return redirect('reset-password', reset_id=reset_id)
            
    except PasswordReset.DoesNotExist:
        
        # redirect to forgot password page if code does not exist
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')

    return render(request, 'reset_password.html')
