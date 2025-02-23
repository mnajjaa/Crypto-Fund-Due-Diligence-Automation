from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home, name='home'),
    path('register/', views.RegisterView, name='register'),
    path('login/', views.LoginView, name='login'),
    path('logout/', views.LogoutView, name='logout'),
    path('forgot-password/', views.ForgotPassword, name='forgot-password'),
    path('password-reset-sent/<str:reset_id>/', views.PasswordResetSent, name='password-reset-sent'),
    path('reset-password/<str:reset_id>/', views.ResetPassword, name='reset-password'),
    path('profile/', views.profile_view, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('delete-profile-picture/', views.delete_profile_picture, name='delete_profile_picture'),
    path('setup-2fa/', views.setup_2fa, name='setup_2fa'),
    path('verify-2fa/', views.verify_2fa_setup, name='verify_2fa_setup'),
    path('disable-2fa/', views.disable_2fa, name='disable_2fa'),  
    path('verify-login/', views.verify_2fa_login, name='verify_2fa_login'),
    path('change-password/', views.change_password, name='change_password'),
    
    ]