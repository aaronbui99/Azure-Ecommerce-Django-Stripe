from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import User, UserProfile


class LoginView(auth_views.LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


class LogoutView(auth_views.LogoutView):
    next_page = 'core:home'


class RegisterView(TemplateView):
    template_name = 'accounts/register.html'
    
    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            return redirect('core:home')
        return render(request, self.template_name, {'form': form})


@method_decorator(login_required, name='dispatch')
class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'


@method_decorator(login_required, name='dispatch')
class ProfileEditView(UpdateView):
    model = User
    template_name = 'accounts/profile_edit.html'
    fields = ['first_name', 'last_name', 'phone', 'street_address', 'city', 'state', 'postal_code', 'country']
    success_url = '/accounts/profile/'
    
    def get_object(self):
        return self.request.user