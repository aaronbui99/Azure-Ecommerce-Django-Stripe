from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
import json
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


# AJAX validation views
@require_http_methods(["POST"])
@csrf_exempt
def check_email_availability(request):
    """AJAX endpoint to check if email is valid and available"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        
        if not email:
            return JsonResponse({
                'is_valid': False,
                'message': 'Email is required.'
            })
        
        # Basic email format validation
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return JsonResponse({
                'is_valid': False,
                'message': 'Please enter a valid email address.'
            })
        
        # Check for common disposable email domains
        disposable_domains = [
            '10minutemail.com', 'tempmail.org', 'guerrillamail.com', 
            'mailinator.com', 'yopmail.com', 'temp-mail.org'
        ]
        domain = email.split('@')[1].lower()
        if domain in disposable_domains:
            return JsonResponse({
                'is_valid': False,
                'message': 'Temporary email addresses are not allowed.'
            })
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'is_valid': False,
                'message': 'This email address is already registered.'
            })
        
        return JsonResponse({
            'is_valid': True,
            'message': 'Email address is available!'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'is_valid': False,
            'message': 'Invalid request format.'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in check_email_availability: {str(e)}")
        return JsonResponse({
            'is_valid': False,
            'message': 'An error occurred while checking email availability.'
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def check_username_availability(request):
    """AJAX endpoint to check if username is available"""
    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        
        if not username:
            return JsonResponse({
                'is_valid': False,
                'message': 'Username is required.'
            })
        
        if len(username) < 3:
            return JsonResponse({
                'is_valid': False,
                'message': 'Username must be at least 3 characters long.'
            })
        
        if len(username) > 150:
            return JsonResponse({
                'is_valid': False,
                'message': 'Username cannot exceed 150 characters.'
            })
        
        # Check if username contains only valid characters (alphanumeric and @/./+/-/_ only)
        import re
        if not re.match(r'^[\w.@+-]+$', username):
            return JsonResponse({
                'is_valid': False,
                'message': 'Username may only contain letters, numbers and @/./+/-/_ characters.'
            })
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'is_valid': False,
                'message': 'This username is already taken.'
            })
        
        return JsonResponse({
            'is_valid': True,
            'message': 'Username is available!'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'is_valid': False,
            'message': 'Invalid request format.'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in check_username_availability: {str(e)}")
        return JsonResponse({
            'is_valid': False,
            'message': 'An error occurred while checking username availability.'
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def validate_password_strength(request):
    """AJAX endpoint to validate password strength"""
    try:
        data = json.loads(request.body)
        password = data.get('password', '')
        
        if not password:
            return JsonResponse({
                'is_valid': False,
                'message': 'Password is required.',
                'strength': 'weak'
            })
        
        # Use Django's built-in password validators
        django_validation_failed = False
        django_errors = []
        try:
            validate_password(password)
        except ValidationError as e:
            django_validation_failed = True
            django_errors = e.messages
        
        # Calculate password strength with detailed analysis
        strength_score = 0
        strength_messages = []
        strength_details = []
        
        # Length check
        if len(password) >= 12:
            strength_score += 2
            strength_details.append('✓ Good length')
        elif len(password) >= 8:
            strength_score += 1
            strength_details.append('✓ Adequate length')
            strength_messages.append('12+ characters for better security')
        else:
            strength_messages.append('at least 8 characters')
        
        # Lowercase check
        if re.search(r'[a-z]', password):
            strength_score += 1
            strength_details.append('✓ Lowercase letters')
        else:
            strength_messages.append('lowercase letters (a-z)')
        
        # Uppercase check
        if re.search(r'[A-Z]', password):
            strength_score += 1
            strength_details.append('✓ Uppercase letters')
        else:
            strength_messages.append('uppercase letters (A-Z)')
        
        # Number check
        if re.search(r'\d', password):
            strength_score += 1
            strength_details.append('✓ Numbers')
        else:
            strength_messages.append('numbers (0-9)')
        
        # Special character check
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            strength_score += 1
            strength_details.append('✓ Special characters')
        else:
            strength_messages.append('special characters (!@#$%^&*)')
        
        # Additional complexity checks
        if len(password) >= 8 and len(set(password)) / len(password) > 0.7:
            strength_score += 1
            strength_details.append('✓ Good character variety')
        elif len(password) >= 8:
            strength_messages.append('more character variety')
        
        # Determine strength level (updated scoring with max of 7 points)
        if strength_score <= 2:
            strength = 'weak'
            color = 'danger'
        elif strength_score <= 4:
            strength = 'medium' 
            color = 'warning'
        else:
            strength = 'strong'
            color = 'success'
        
        # Prepare suggestions and details
        suggestions_msg = ''
        if strength_messages:
            suggestions_msg = f"Add: {', '.join(strength_messages)}"
        
        details_msg = ''
        if strength_details:
            details_msg = ' | '.join(strength_details)
        
        # Determine if password is truly invalid
        is_valid = not django_validation_failed and strength != 'weak'
        
        # Prepare message based on validation results
        if django_validation_failed:
            message = ' '.join(django_errors)
        else:
            message = f'Password strength: {strength.capitalize()}'
            if details_msg:
                message += f' ({strength_score}/7 points)'
        
        return JsonResponse({
            'is_valid': is_valid,
            'message': message,
            'strength': strength,
            'color': color,
            'suggestions': suggestions_msg,
            'details': details_msg,
            'score': strength_score,
            'max_score': 7,
            'django_error': django_validation_failed
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'is_valid': False,
            'message': 'Invalid request format.',
            'strength': 'weak'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in validate_password_strength: {str(e)}")
        return JsonResponse({
            'is_valid': False,
            'message': 'An error occurred while validating password.',
            'strength': 'weak'
        }, status=500)