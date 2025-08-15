from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth import login
from django.contrib import messages
import logging
from .models import User, UserProfile
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm

# Configure logging
logger = logging.getLogger(__name__)


class LoginView(auth_views.LoginView):
    template_name = 'accounts/login.html'
    form_class = CustomAuthenticationForm
    redirect_authenticated_user = True


class LogoutView(auth_views.LogoutView):
    next_page = 'core:home'


class RegisterView(TemplateView):
    template_name = 'accounts/register.html'
    
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        
        # Log password to command prompt for debugging
        if 'password1' in request.POST:
            password = request.POST['password1']

        if form.is_valid():
            user = form.save()
            
            # Create user profile
            UserProfile.objects.get_or_create(user=user)
            # Explicitly specify the backend since multiple auth backends are configured
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Account created successfully! Welcome to Azure E-commerce.')
            return redirect('core:home')
        return render(request, self.template_name, {'form': form})


@method_decorator(login_required, name='dispatch')
class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'


@method_decorator(login_required, name='dispatch')
class ProfileEditView(UpdateView):
    model = User
    template_name = 'accounts/profile_edit.html'
    form_class = UserProfileForm
    success_url = '/accounts/profile/'
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)