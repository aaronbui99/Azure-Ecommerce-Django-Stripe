// Register page validation JavaScript
// This file handles email, username, and password validation with real-time feedback

class RegisterValidation {
    constructor(form) {
        this.form = form;
        this.config = this.getConfigFromDataAttributes();
        this.initElements();
        this.initEventListeners();
        this.emailTimeout = null;
        this.usernameTimeout = null;
    }

    getConfigFromDataAttributes() {
        return {
            checkEmailUrl: this.form.dataset.checkEmailUrl,
            checkUsernameUrl: this.form.dataset.checkUsernameUrl,
            validatePasswordUrl: this.form.dataset.validatePasswordUrl,
            usernameFieldId: this.form.dataset.usernameFieldId,
            passwordFieldId: this.form.dataset.passwordFieldId
        };
    }

    initElements() {
        // Form elements
        this.emailInput = document.getElementById('id_email');
        this.usernameInput = document.getElementById(this.config.usernameFieldId);
        this.passwordInput = document.getElementById(this.config.passwordFieldId);
        
        // Email validation elements
        this.emailSpinner = document.getElementById('email-spinner');
        this.emailCheck = document.getElementById('email-check');
        this.emailCross = document.getElementById('email-cross');
        this.emailFeedback = document.getElementById('email-feedback');
        
        // Username validation elements
        this.usernameSpinner = document.getElementById('username-spinner');
        this.usernameCheck = document.getElementById('username-check');
        this.usernameCross = document.getElementById('username-cross');
        this.usernameFeedback = document.getElementById('username-feedback');
        
        // Password validation elements
        this.strengthBar = document.getElementById('strength-bar');
        this.passwordFeedback = document.getElementById('password-feedback');
        this.passwordSuggestions = document.getElementById('password-suggestions');
        
        // Form element (already set in constructor)
    }

    initEventListeners() {
        // Email validation
        if (this.emailInput) {
            this.emailInput.addEventListener('input', (e) => {
                this.handleEmailInput(e.target.value.trim());
            });
        }

        // Username validation
        if (this.usernameInput) {
            this.usernameInput.addEventListener('input', (e) => {
                this.handleUsernameInput(e.target.value.trim());
            });
        }

        // Password validation
        if (this.passwordInput) {
            this.passwordInput.addEventListener('input', (e) => {
                this.handlePasswordInput(e.target.value);
            });
        }

        // Form submit handling
        if (this.form) {
            this.form.addEventListener('submit', () => {
                this.clearValidationStates();
            });
        }
    }

    // Utility function to get CSRF token
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    // Email validation
    handleEmailInput(email) {
        clearTimeout(this.emailTimeout);
        
        if (email.length === 0) {
            this.resetEmailIndicators();
            return;
        }
        
        this.emailTimeout = setTimeout(() => {
            this.validateEmail(email);
        }, 500);
    }

    validateEmail(email) {
        // Show spinner
        this.emailSpinner.classList.remove('d-none');
        this.emailCheck.classList.add('d-none');
        this.emailCross.classList.add('d-none');
        
        fetch(this.config.checkEmailUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            },
            body: JSON.stringify({email: email})
        })
        .then(response => response.json())
        .then(data => {
            this.emailSpinner.classList.add('d-none');
            
            if (data.is_valid) {
                this.showEmailSuccess(data.message);
            } else {
                this.showEmailError(data.message);
            }
        })
        .catch(error => {
            console.error('Error validating email:', error);
            this.showEmailNetworkError();
        });
    }

    showEmailSuccess(message) {
        this.emailCheck.classList.remove('d-none');
        this.emailCheck.classList.add('success-icon');
        this.emailCross.classList.add('d-none');
        this.emailFeedback.textContent = message;
        this.emailFeedback.className = 'small mt-1 validation-success';
        this.emailInput.classList.remove('is-invalid');
        this.emailInput.classList.add('is-valid');
    }

    showEmailError(message) {
        this.emailCheck.classList.add('d-none');
        this.emailCross.classList.remove('d-none');
        this.emailCross.classList.add('error-icon');
        
        this.emailFeedback.innerHTML = `
            <div class="invalid-input-message">
                <i class="fas fa-envelope-open-text me-1"></i>
                Invalid Email
            </div>
            <div class="validation-error small mt-1">${message}</div>
        `;
        this.emailInput.classList.remove('is-valid');
        this.emailInput.classList.add('is-invalid');
    }

    showEmailNetworkError() {
        this.emailSpinner.classList.add('d-none');
        this.emailCross.classList.remove('d-none');
        this.emailCross.classList.add('error-icon');
        
        this.emailFeedback.innerHTML = `
            <div class="invalid-input-message">
                <i class="fas fa-wifi me-1"></i>
                Connection Error
            </div>
            <div class="validation-error small mt-1">Error checking email availability</div>
        `;
    }

    resetEmailIndicators() {
        this.emailSpinner.classList.add('d-none');
        this.emailCheck.classList.add('d-none');
        this.emailCheck.classList.remove('success-icon');
        this.emailCross.classList.add('d-none');
        this.emailCross.classList.remove('error-icon');
        this.emailFeedback.innerHTML = '';
        this.emailInput.classList.remove('is-valid', 'is-invalid');
    }

    // Username validation
    handleUsernameInput(username) {
        clearTimeout(this.usernameTimeout);
        
        if (username.length === 0) {
            this.resetUsernameIndicators();
            return;
        }
        
        this.usernameTimeout = setTimeout(() => {
            this.validateUsername(username);
        }, 500);
    }

    validateUsername(username) {
        // Show spinner
        this.usernameSpinner.classList.remove('d-none');
        this.usernameCheck.classList.add('d-none');
        this.usernameCross.classList.add('d-none');
        
        fetch(this.config.checkUsernameUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            },
            body: JSON.stringify({username: username})
        })
        .then(response => response.json())
        .then(data => {
            this.usernameSpinner.classList.add('d-none');
            
            if (data.is_valid) {
                this.showUsernameSuccess(data.message);
            } else {
                this.showUsernameError(data.message);
            }
        })
        .catch(error => {
            console.error('Error validating username:', error);
            this.showUsernameNetworkError();
        });
    }

    showUsernameSuccess(message) {
        this.usernameCheck.classList.remove('d-none');
        this.usernameCheck.classList.add('success-icon');
        this.usernameCross.classList.add('d-none');
        this.usernameFeedback.textContent = message;
        this.usernameFeedback.className = 'small mt-1 validation-success';
        this.usernameInput.classList.remove('is-invalid');
        this.usernameInput.classList.add('is-valid');
    }

    showUsernameError(message) {
        this.usernameCheck.classList.add('d-none');
        this.usernameCross.classList.remove('d-none');
        this.usernameCross.classList.add('error-icon');
        
        this.usernameFeedback.innerHTML = `
            <div class="invalid-input-message">
                <i class="fas fa-exclamation-triangle me-1"></i>
                Invalid Input
            </div>
            <div class="validation-error small mt-1">${message}</div>
        `;
        this.usernameInput.classList.remove('is-valid');
        this.usernameInput.classList.add('is-invalid');
    }

    showUsernameNetworkError() {
        this.usernameSpinner.classList.add('d-none');
        this.usernameCross.classList.remove('d-none');
        this.usernameCross.classList.add('error-icon');
        
        this.usernameFeedback.innerHTML = `
            <div class="invalid-input-message">
                <i class="fas fa-wifi me-1"></i>
                Connection Error
            </div>
            <div class="validation-error small mt-1">Error checking username availability</div>
        `;
    }

    resetUsernameIndicators() {
        this.usernameSpinner.classList.add('d-none');
        this.usernameCheck.classList.add('d-none');
        this.usernameCheck.classList.remove('success-icon');
        this.usernameCross.classList.add('d-none');
        this.usernameCross.classList.remove('error-icon');
        this.usernameFeedback.innerHTML = '';
        this.usernameInput.classList.remove('is-valid', 'is-invalid');
    }

    // Password validation
    handlePasswordInput(password) {
        this.validatePassword(password);
    }

    validatePassword(password) {
        if (!password) {
            this.resetPasswordIndicators();
            return;
        }
        
        fetch(this.config.validatePasswordUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            },
            body: JSON.stringify({password: password})
        })
        .then(response => response.json())
        .then(data => {
            this.updatePasswordStrength(data);
            this.updatePasswordSuggestions(data);
            this.updatePasswordFeedback(data);
        })
        .catch(error => {
            console.error('Error validating password:', error);
            this.showPasswordNetworkError();
        });
    }

    updatePasswordStrength(data) {
        this.strengthBar.className = `strength-bar strength-${data.strength}`;
    }

    updatePasswordSuggestions(data) {
        let suggestionsHtml = '';
        if (data.suggestions) {
            suggestionsHtml += `<div><i class="fas fa-lightbulb me-1"></i><strong>Improve:</strong> ${data.suggestions}</div>`;
        }
        if (data.details) {
            suggestionsHtml += `<div class="mt-1"><i class="fas fa-info-circle me-1"></i>${data.details}</div>`;
        }
        
        this.passwordSuggestions.innerHTML = suggestionsHtml;
        this.passwordSuggestions.className = 'small mt-1 text-muted';
    }

    updatePasswordFeedback(data) {
        if (data.is_valid && data.strength === 'strong') {
            this.showPasswordSuccess(data);
        } else if (!data.is_valid) {
            this.showPasswordError(data);
        } else {
            this.showPasswordWarning(data);
        }
    }

    showPasswordSuccess(data) {
        this.passwordInput.classList.remove('is-invalid');
        this.passwordInput.classList.add('is-valid');
        this.passwordFeedback.innerHTML = `
            <div class="validation-success small">
                <i class="fas fa-check-circle me-1"></i>${data.message}
            </div>
            <div class="password-progress">
                <i class="fas fa-chart-bar me-1"></i>Strength: ${data.score}/${data.max_score} points
            </div>
        `;
    }

    showPasswordError(data) {
        this.passwordInput.classList.remove('is-valid');
        this.passwordInput.classList.add('is-invalid');
        
        if (data.django_error) {
            this.passwordFeedback.innerHTML = `
                <div class="invalid-input-message">
                    <i class="fas fa-exclamation-triangle me-1"></i>
                    Invalid Password
                </div>
                <div class="validation-error small mt-1">${data.message}</div>
            `;
        } else if (data.strength === 'weak') {
            this.passwordFeedback.innerHTML = `
                <div class="invalid-input-message">
                    <i class="fas fa-shield-alt me-1"></i>
                    Weak Password
                </div>
                <div class="validation-error small mt-1">${data.message}</div>
                <div class="password-progress">
                    <i class="fas fa-chart-bar me-1"></i>Strength: ${data.score}/${data.max_score} points
                </div>
            `;
        }
    }

    showPasswordWarning(data) {
        this.passwordInput.classList.remove('is-valid', 'is-invalid');
        this.passwordFeedback.innerHTML = `
            <div class="validation-warning small">
                <i class="fas fa-exclamation-circle me-1"></i>${data.message}
            </div>
            <div class="password-progress">
                <i class="fas fa-chart-bar me-1"></i>Strength: ${data.score}/${data.max_score} points
            </div>
        `;
    }

    showPasswordNetworkError() {
        this.passwordFeedback.innerHTML = `
            <div class="invalid-input-message">
                <i class="fas fa-wifi me-1"></i>
                Connection Error
            </div>
            <div class="validation-error small mt-1">Error checking password strength</div>
        `;
    }

    resetPasswordIndicators() {
        this.strengthBar.className = 'strength-bar';
        this.passwordFeedback.innerHTML = '';
        this.passwordSuggestions.innerHTML = '';
        this.passwordInput.classList.remove('is-valid', 'is-invalid');
    }

    clearValidationStates() {
        // Clear AJAX validation classes to prevent conflicts with Django form validation
        if (this.emailInput) this.emailInput.classList.remove('is-valid', 'is-invalid');
        if (this.usernameInput) this.usernameInput.classList.remove('is-valid', 'is-invalid');
        if (this.passwordInput) this.passwordInput.classList.remove('is-valid', 'is-invalid');
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Find the form with validation data attributes
    const form = document.querySelector('form[data-check-email-url]');
    if (form) {
        new RegisterValidation(form);
    }
});