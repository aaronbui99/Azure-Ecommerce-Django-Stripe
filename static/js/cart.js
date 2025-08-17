// Global cart functionality
class CartManager {
    constructor() {
        this.cartCountElement = document.getElementById('cart-count');
        this.init();
    }

    init() {
        // Load initial cart count
        this.loadCartCount();
        
        // Handle add to cart forms
        this.setupAddToCartForms();
        
        // Handle quantity updates on cart page
        this.setupCartUpdates();
    }

    async loadCartCount() {
        try {
            const response = await fetch('/api/v1/orders/cart-count/');
            const data = await response.json();
            
            if (data.success && this.cartCountElement) {
                this.cartCountElement.textContent = data.cart_total;
            }
        } catch (error) {
            console.error('Error loading cart count:', error);
        }
    }

    setupAddToCartForms() {
        // Handle all add-to-cart forms on the page
        document.addEventListener('submit', async (e) => {
            if (e.target.matches('form[action*="add_to_cart"], .add-to-cart-form')) {
                e.preventDefault();
                
                const form = e.target;
                const submitButton = form.querySelector('button[type="submit"]');
                const originalText = submitButton.innerHTML;
                
                // Show loading state
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Adding...';
                submitButton.disabled = true;
                
                try {
                    const formData = new FormData(form);
                    
                    const response = await fetch(form.action, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        // Update cart count
                        if (this.cartCountElement) {
                            this.cartCountElement.textContent = data.cart_total;
                        }
                        
                        // Show success message
                        this.showMessage(data.message, 'success');
                        
                        // Reset button
                        submitButton.innerHTML = '<i class="fas fa-check me-2"></i>Added!';
                        submitButton.classList.remove('btn-primary');
                        submitButton.classList.add('btn-success');
                        
                        // Reset button after delay
                        setTimeout(() => {
                            submitButton.innerHTML = originalText;
                            submitButton.classList.remove('btn-success');
                            submitButton.classList.add('btn-primary');
                            submitButton.disabled = false;
                        }, 2000);
                        
                    } else {
                        this.showMessage(data.message || 'Error adding to cart', 'danger');
                        submitButton.innerHTML = originalText;
                        submitButton.disabled = false;
                    }
                } catch (error) {
                    console.error('Error adding to cart:', error);
                    this.showMessage('Error adding to cart', 'danger');
                    submitButton.innerHTML = originalText;
                    submitButton.disabled = false;
                }
            }
        });
    }

    setupCartUpdates() {
        // Handle quantity updates on cart page
        document.addEventListener('input', async (e) => {
            if (e.target.matches('input[data-item-id], .quantity-input')) {
                const input = e.target;
                const itemId = input.dataset.itemId;
                const quantity = Math.max(0, Math.min(99, parseInt(input.value) || 0));
                
                if (quantity >= 0) {
                    await this.updateCartItem(itemId, quantity);
                }
            }
        });

        // Handle cart buttons (quantity +/-, remove) on cart page
        document.addEventListener('click', async (e) => {
            // Handle quantity buttons (+ and - buttons)
            if (e.target.matches('.quantity-btn')) {
                e.preventDefault();
                
                const button = e.target;
                const itemId = button.dataset.itemId;
                const action = button.dataset.action;
                const input = document.querySelector(`input[data-item-id="${itemId}"]`);
                
                if (input) {
                    let newQuantity = parseInt(input.value);
                    if (action === 'increase') {
                        newQuantity = Math.min(newQuantity + 1, 99);
                    } else if (action === 'decrease') {
                        newQuantity = Math.max(newQuantity - 1, 0);
                    }
                    
                    await this.updateCartItem(itemId, newQuantity);
                }
            }
            // Handle remove buttons
            else if (e.target.matches('.remove-btn, .remove-btn *')) {
                e.preventDefault();
                
                const button = e.target.closest('.remove-btn');
                const itemId = button.dataset.itemId;
                
                if (confirm('Are you sure you want to remove this item?')) {
                    await this.updateCartItem(itemId, 0);
                }
            }
        });
    }

    async updateCartItem(itemId, quantity) {
        try {
            const response = await fetch('/api/v1/orders/update-cart/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    item_id: itemId,
                    quantity: quantity
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                if (quantity === 0) {
                    // Remove the item row
                    const itemRow = document.querySelector(`[data-item-id="${itemId}"]`);
                    if (itemRow) {
                        itemRow.remove();
                    }
                } else {
                    // Update quantity input
                    const quantityInput = document.querySelector(`input[data-item-id="${itemId}"]`);
                    if (quantityInput) {
                        quantityInput.value = quantity;
                    }
                }
                
                // Update cart totals if elements exist
                const subtotalElement = document.getElementById('cart-subtotal');
                const totalElement = document.getElementById('cart-total');
                
                if (subtotalElement) {
                    subtotalElement.textContent = `$${data.subtotal}`;
                }
                if (totalElement) {
                    totalElement.textContent = `$${data.subtotal}`;
                }
                
                // Update cart count in navbar
                if (this.cartCountElement) {
                    this.cartCountElement.textContent = data.cart_total;
                }
                
                // Reload page if cart is empty
                if (data.cart_total === 0) {
                    location.reload();
                }
                
                this.showMessage(data.message, 'success');
            } else {
                this.showMessage(data.message || 'Error updating cart', 'danger');
            }
        } catch (error) {
            console.error('Error updating cart:', error);
            this.showMessage('Error updating cart', 'danger');
        }
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    showMessage(message, type) {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Find or create messages container
        let messagesContainer = document.querySelector('.messages-container');
        if (!messagesContainer) {
            messagesContainer = document.createElement('div');
            messagesContainer.className = 'messages-container container mt-3';
            
            const mainElement = document.querySelector('main');
            if (mainElement) {
                mainElement.parentNode.insertBefore(messagesContainer, mainElement);
            } else {
                document.body.insertBefore(messagesContainer, document.body.firstChild);
            }
        }
        
        // Add the alert
        messagesContainer.appendChild(alertDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

// Initialize cart manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CartManager();
});