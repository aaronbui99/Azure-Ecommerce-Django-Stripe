# Stripe Payment Testing Guide

This guide helps you test the payment functionality using Stripe's test cards.

## Prerequisites

1. Make sure you're in **DEBUG mode** (check `settings.DEBUG = True`)
2. Use **Stripe test keys** (not live keys)
3. Have a user account to test with

## Quick Start

### Option 1: Create Test Order via URL
1. Login to the application
2. Visit `/payments/test-order/` 
3. This will create a test order and redirect you to payment processing

### Option 2: Manual Flow
1. Add products to cart
2. Go through checkout process
3. Complete billing/shipping information
4. Get redirected to payment page

### Option 3: Direct Payment Page
1. Login to the application  
2. Visit `/payments/process/`
3. If no order exists, click "Create Test Order" button

## Stripe Test Cards

### ✅ Success Cards
Use these cards to test successful payments:

| Card Number | Brand | CVC | Expiry | Zip |
|-------------|--------|-----|---------|-----|
| `4242 4242 4242 4242` | Visa | Any 3 digits | Any future date | Any 5 digits |
| `5555 5555 5555 4444` | Mastercard | Any 3 digits | Any future date | Any 5 digits |
| `3782 8224 6310 005` | American Express | Any 4 digits | Any future date | Any 5 digits |

### 🔐 3D Secure / Authentication Required
These cards require additional authentication:

| Card Number | Description | CVC | Expiry |
|-------------|-------------|-----|---------|
| `4000 0027 6000 3184` | Always requires authentication | Any 3 digits | Any future date |
| `4000 0025 0000 3155` | 3D Secure optional | Any 3 digits | Any future date |

### ❌ Decline Cards  
Use these to test various decline scenarios:

| Card Number | Decline Reason | CVC | Expiry |
|-------------|----------------|-----|---------|
| `4000 0000 0000 0002` | Generic decline | Any 3 digits | Any future date |
| `4000 0000 0000 9995` | Insufficient funds | Any 3 digits | Any future date |
| `4000 0000 0000 9987` | Lost card | Any 3 digits | Any future date |
| `4000 0000 0000 9979` | Stolen card | Any 3 digits | Any future date |
| `4000 0000 0000 0069` | Expired card | Any 3 digits | Any future date |
| `4000 0000 0000 0127` | Incorrect CVC | Any 3 digits | Any future date |

### ⚠️ Processing Errors
Test processing and validation errors:

| Card Number | Error Type | CVC | Expiry |
|-------------|------------|-----|---------|
| `4000 0000 0000 0119` | Processing error | Any 3 digits | Any future date |
| `4242 4242 4242 4241` | Incorrect number | Any 3 digits | Any future date |

## How to Test

### Using the Test Card Interface

1. **Visit the payment page** - The test card interface appears automatically in DEBUG mode
2. **Click a test card button** - This copies the card number to clipboard and shows details
3. **Paste into payment form** - Paste the card number and enter the displayed expiry/CVC
4. **Submit payment** - Test the various scenarios

### Manual Entry

1. **Enter card details manually** into the Stripe payment form
2. **Use any future expiry date** (e.g., 12/25, 06/26)
3. **Use any 3-digit CVC** for Visa/MC, 4-digit for Amex  
4. **Use any valid ZIP code** (e.g., 12345)

## Testing Scenarios

### 1. Successful Payment Flow
```
Card: 4242 4242 4242 4242
Expected: Payment succeeds, order status changes to 'confirmed'
```

### 2. Insufficient Funds
```
Card: 4000 0000 0000 9995  
Expected: Payment fails with "insufficient funds" error
```

### 3. 3D Secure Authentication
```
Card: 4000 0027 6000 3184
Expected: Additional authentication popup appears
```

### 4. Generic Decline
```
Card: 4000 0000 0000 0002
Expected: Payment fails with generic decline message
```

## Webhook Testing

Stripe sends webhooks for payment events. Test these locally:

1. **Install Stripe CLI**: `stripe listen --forward-to localhost:8000/payments/webhook/`
2. **Update webhook secret** in `.env` file
3. **Test payments** to trigger webhook events
4. **Check logs** for webhook processing

## Debugging

### Payment Not Loading
- Check browser console for JavaScript errors
- Verify Stripe public key is set in settings
- Ensure order exists in session
- Check DEBUG mode is enabled

### Payment Failing
- Verify Stripe secret key is correct
- Check order exists and belongs to current user
- Ensure sufficient order total (minimum $0.50)
- Check network tab for API errors

### Console Debugging
Open browser console to see debug messages:
- Order existence check
- Stripe initialization
- Card element mounting
- Payment processing steps

## Order Management

### View Orders
- Admin panel: `/admin/orders/order/`
- User orders: `/orders/`

### Order States
- `pending` - Awaiting payment
- `confirmed` - Payment successful  
- `processing` - Being prepared
- `shipped` - Shipped to customer

## Security Notes

⚠️ **Important Security Reminders:**

1. **Never use real card numbers** in test mode
2. **Never commit Stripe secret keys** to version control  
3. **Always use test keys** for development
4. **Validate all payments** server-side
5. **Use HTTPS** in production

## Troubleshooting

### Common Issues

**"No order found"**
- Create test order via `/payments/test-order/`
- Or go through checkout flow first

**"Stripe key missing"**  
- Check `.env` file has `STRIPE_PUBLISHABLE_KEY`
- Verify settings.py loads environment variables

**"Card element not loading"**
- Check browser console for errors
- Verify Stripe.js is loading from CDN
- Ensure proper content security policy

**Payment intent creation fails**
- Check Stripe secret key is valid
- Verify order total is above minimum
- Check server logs for detailed errors

## Support Resources

- [Stripe Testing Documentation](https://docs.stripe.com/testing)
- [Stripe Dashboard (Test Mode)](https://dashboard.stripe.com/test)
- [Stripe API Reference](https://docs.stripe.com/api)
- [Django Stripe Integration](https://testdriven.io/blog/django-stripe-tutorial/)

---

**Happy Testing! 🚀**