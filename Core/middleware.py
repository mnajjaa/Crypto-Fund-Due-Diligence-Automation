import logging
from django.shortcuts import redirect
from django.urls import resolve
from django_otp.plugins.otp_totp.models import TOTPDevice
from .models import Profile


logger = logging.getLogger(__name__)

class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log incoming requests
        logger.info(f"Incoming request: {request.path}")
        response = self.get_response(request)
        return response

class Require2FAMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # List of exempt URL names
        exempt_url_names = [
            'home', 'login', 'register', 'logout',
            'setup_2fa', 'verify_2fa_setup', 'disable_2fa',
            'verify_2fa_login', 'password-reset-sent', 'reset-password'
        ]
        
        # Skip middleware for anonymous users
        if not request.user.is_authenticated:
            return None

        # Skip if 2FA is already verified
        if request.session.get('2fa_verified'):
            return None

        try:
            # Get the current URL name
            url_name = resolve(request.path_info).url_name
        except:
            # If URL resolution fails, allow the request
            return None

        # Check if the current URL is exempt
        if url_name in exempt_url_names:
            return None

        # Check if 2FA is enabled for the user
        profile = Profile.objects.get(user=request.user)
        if profile.is_2fa_enabled:
            logger.info(f"Redirecting {request.user} to 2FA verification")
            return redirect('verify_2fa_login')

        return None