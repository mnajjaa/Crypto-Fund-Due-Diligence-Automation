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
from .forms import ProfileForm
from .models import Profile
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp import devices_for_user
import qrcode
import qrcode.image.svg
from io import BytesIO
import pyotp
import qrcode
from io import BytesIO
import base64
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ChangePasswordForm
import re



@login_required 
def Home(request):
    access_token = request.GET.get('access_token', None)
    return render(request, 'index.html', {'access_token': access_token})

def RegisterView(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')  
        password = request.POST.get('password')

        user_data_has_error = False

        # Check if username or email is taken
        if User.objects.filter(username=username).exists():
            user_data_has_error = True
            messages.error(request, 'Username already exists')

        if User.objects.filter(email=email).exists():
            user_data_has_error = True
            messages.error(request, 'Email already exists')

        # Password validation: Min 6 chars, 1 number, 1 special character
        if len(password) < 6 or not re.search(r"\d", password) or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            user_data_has_error = True
            messages.error(request, 'Password must be at least 6 characters long, contain at least one number, and one special character.')

        if user_data_has_error:
            return redirect('register')
        else:
            new_user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password
            )
            messages.success(request, "Account created. Login now")
            return redirect('login')

    return render(request, 'sign-up.html')

def LoginView(request):
    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # login user if login credentials are correct
            login(request, user)
            profile = Profile.objects.get(user=user)
            if profile.is_2fa_enabled:
                return redirect('verify_2fa_login') 
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # ewdirect to home page
            return redirect(f"/?access_token={access_token}")

        else:
            messages.error(request, 'Invalid user credentials')
            return redirect('login')


    return render(request, 'sign-in.html')



def LogoutView(request):
    if '2fa_verified' in request.session:
        del request.session['2fa_verified'] 
    logout(request)
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

    return render(request, 'forgot_password.html')

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

@login_required
def profile_view(request):
    profile = Profile.objects.get(user=request.user)  # Fetch the profile
    return render(request, 'profile.html', {'profile': profile})

@login_required
def edit_profile(request):
    profile = request.user.profile
    user = request.user  

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile, user=user)  # Pass user here
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user  # Ensure it's linked
            profile.save()

            # Update User fields
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.save()

            messages.success(request, "Profile updated successfully")
            return redirect('profile')  
    else:
        form = ProfileForm(instance=profile, user=user)  # Pass user here

    return render(request, 'profile.html', {'form': form, 'profile': profile})

  

@login_required
def setup_2fa(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    # Generate a new OTP secret if one doesn't exist
    if not profile.otp_secret:
        profile.otp_secret = pyotp.random_base32()
        profile.save()

    # Generate a provisioning URI for the authenticator app
    totp = pyotp.TOTP(profile.otp_secret)
    provisioning_uri = totp.provisioning_uri(name=request.user.email, issuer_name="DueDiligence")

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert QR code to base64 for embedding in HTML
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

    return JsonResponse({
        'success': True,
        'qr_code_base64': qr_code_base64
    })

@login_required
def verify_2fa_setup(request):
    if request.method == 'POST':
        profile = Profile.objects.get(user=request.user)
        totp = pyotp.TOTP(profile.otp_secret)
        token = request.POST.get('token')

        if totp.verify(token):
            profile.is_2fa_enabled = True  # Update this field
            profile.save()  # Save the changes
            #messages.success(request, '2FA successfully enabled!')
            return redirect('profile')
        else:
            messages.error(request, 'Invalid token. Please try again.')
            return redirect('setup_2fa')

@login_required
def verify_2fa_login(request):
    if request.method == 'POST':
        profile = Profile.objects.get(user=request.user)
        totp = pyotp.TOTP(profile.otp_secret)

        # Collect the six digits from the form
        token = ''.join([request.POST.get(f'token_{i}', '') for i in range(1, 7)])

        if totp.verify(token):
            request.session['2fa_verified'] = True
            return redirect('home')
        else:
            messages.error(request, 'Invalid code')
    return render(request, 'verify_login_2fa.html')

@login_required
def disable_2fa(request):
    if request.method == 'POST':
        profile = Profile.objects.get(user=request.user)
        profile.is_2fa_enabled = False
        profile.otp_secret = ''  # Clear the OTP secret
        profile.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            current_password = form.cleaned_data['current_password']
            new_password = form.cleaned_data['new_password']

            # Verify the current password
            if not request.user.check_password(current_password):
                messages.error(request, "Your current password is incorrect.")
            else:
                # Set the new password
                request.user.set_password(new_password)
                request.user.save()

                # Update the session to prevent the user from being logged out
                update_session_auth_hash(request, request.user)

                messages.success(request, "Your password has been changed successfully.")
                return redirect('profile')  # Redirect to the profile page
        else:
            # If the form is invalid, display error messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ChangePasswordForm()

    return redirect('profile')