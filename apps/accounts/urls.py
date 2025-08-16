from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    
    # AJAX validation endpoints
    path('ajax/check-email/', views.check_email_availability, name='check_email'),
    path('ajax/check-username/', views.check_username_availability, name='check_username'),
    path('ajax/validate-password/', views.validate_password_strength, name='validate_password'),
]