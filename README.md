# Azure-Ecommerce-Django-Stripe

***************************** IN DEVELOPMENT NOT DONE (Aaron Bui 8/15/2025) *******************************************
A modern Django-based e-commerce platform designed for global deployment on Microsoft Azure with Stripe payment integration. The architecture follows a "Monolith-first" approach with Active-Active configuration for global low-latency with minimal operations overhead.

## 🚀 Features

- **Complete E-commerce Solution**: Product catalog, shopping cart, order management, and customer accounts
- **Secure Payment Processing**: Stripe integration with support for cards, wallets, and bank transfers
- **Azure Cloud Native**: Built for Azure App Service with SQL Database, Redis Cache, and Blob Storage
- **Global Scale Ready**: Active-Active architecture with Azure Front Door for worldwide distribution
- **Enterprise Security**: WAF, private endpoints, CSP headers, and comprehensive security defaults
- **RESTful API**: Full API coverage with Django REST Framework
- **Admin Dashboard**: Feature-rich admin interface for complete store management
- **Responsive Design**: Mobile-first Bootstrap 5 interface

## 🏗️ Technology Stack

- **Backend**: Django 4.2+ with Python 3.9+
- **Database**: Azure SQL Database with geo-replication and read replica support
- **Cache**: Azure Cache for Redis Enterprise with Active-Geo Replication
- **Storage**: Azure Blob Storage with RA-GRS for global media distribution
- **Payments**: Stripe Payment Intents API with webhook support
- **Authentication**: Django Auth system with Azure B2C integration ready
- **Frontend**: Bootstrap 5 with responsive, mobile-first design
- **API**: Django REST Framework with comprehensive serializers
- **Monitoring**: Application Insights integration for observability

## ⚡ Quick Start

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+** - [Download Python](https://python.org/downloads/)
- **Git** - [Download Git](https://git-scm.com/downloads/)
- **Azure Account** - [Create free account](https://azure.microsoft.com/free/) (for production)
- **Stripe Account** - [Sign up](https://stripe.com/) (for payment processing)

### 🔧 Local Development Setup

#### Step 1: Clone and Setup Project

```bash
# Clone the repository
git clone https://github.com/aaronbui99/Azure-Ecommerce-Django-Stripe.git
cd Azure-Ecommerce-Django-Stripe

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows Command Prompt
venv\Scripts\activate
# Windows PowerShell
venv\Scripts\Activate.ps1
# macOS/Linux
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip
```

#### Step 2: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
python -c "import django; print('Django version:', django.get_version())"
```

#### Step 3: Environment Configuration

```bash
# Copy environment template
copy .env.example .env     # Windows
cp .env.example .env       # macOS/Linux

# Edit .env file with your settings
# Use your preferred text editor
notepad .env              # Windows
nano .env                 # Linux
code .env                 # VS Code
```

**Essential .env configuration for local development:**

```env
# Basic Django Settings
DEBUG=True
SECRET_KEY=your-super-secret-key-change-this-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for local development)
PRIMARY_SQL_URL=sqlite:///db.sqlite3
READ_SQL_URL=sqlite:///db.sqlite3

# Redis (optional for local development)
REDIS_URL=redis://127.0.0.1:6379/1
REDIS_SSL=False

# Azure Storage (optional for local development)
USE_AZURE_STORAGE=False

# Stripe Configuration (get from your Stripe dashboard)
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key_here
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Security Settings for development
SECURE_SSL_REDIRECT=False
DJANGO_LOG_LEVEL=DEBUG
```

#### Step 4: Database Setup

```bash
# Create initial migrations for custom apps
python manage.py makemigrations accounts
python manage.py makemigrations products
python manage.py makemigrations orders
python manage.py makemigrations payments

# Apply all migrations
python manage.py migrate

# Create superuser account
python manage.py createsuperuser
# Follow prompts to set username, email, and password
```

#### Step 5: Load Sample Data (Optional)

```bash
# Create sample categories and products for testing
python manage.py shell
```

Then in the Django shell:

```python
from apps.products.models import Category, Product, ProductImage
from apps.accounts.models import User
from decimal import Decimal

# Create sample categories
electronics = Category.objects.create(name="Electronics", description="Electronic devices and gadgets")
clothing = Category.objects.create(name="Clothing", description="Fashion and apparel")
books = Category.objects.create(name="Books", description="Books and literature")

# Create sample products
Product.objects.create(
    name="Smartphone",
    category=electronics,
    description="Latest smartphone with advanced features",
    price=Decimal('699.99'),
    sku="PHONE-001",
    inventory_quantity=50
)

Product.objects.create(
    name="Laptop",
    category=electronics,
    description="High-performance laptop for work and gaming",
    price=Decimal('1299.99'),
    sku="LAPTOP-001",
    inventory_quantity=25
)

Product.objects.create(
    name="T-Shirt",
    category=clothing,
    description="Comfortable cotton t-shirt",
    price=Decimal('29.99'),
    sku="SHIRT-001",
    inventory_quantity=100
)

print("Sample data created successfully!")
exit()
```

#### Step 6: Run Development Server

```bash
# Start the development server
python manage.py runserver

# Server will start at http://127.0.0.1:8000/
# Admin panel available at http://127.0.0.1:8000/admin/
# API endpoints at http://127.0.0.1:8000/api/
```

### 🌐 Access Your Application

Once the server is running, you can access:

- **Homepage**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/ (use superuser credentials)
- **Products**: http://127.0.0.1:8000/products/
- **API Documentation**: http://127.0.0.1:8000/api/
- **Health Check**: http://127.0.0.1:8000/health/

## 🛠️ Development Workflow

### Running Tests

```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test apps.products

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Creates htmlcov/index.html
```

### Database Management

```bash
# Create new migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (CAUTION: Destroys all data)
python manage.py flush

# Load fixtures
python manage.py loaddata fixtures/sample_data.json
```

### Static Files

```bash
# Collect static files for production
python manage.py collectstatic

# During development, files are served automatically
# No need to run collectstatic for local development
```

## 📁 Project Structure

```
Azure-Ecommerce-Django-Stripe/
├── 📁 apps/                          # Django applications
│   ├── 📁 accounts/                 # User management & authentication
│   │   ├── 📁 migrations/          # Database migrations
│   │   ├── 📄 models.py            # User and Profile models
│   │   ├── 📄 views.py             # Authentication views
│   │   └── 📄 admin.py             # Admin configuration
│   ├── 📁 core/                    # Core functionality
│   │   ├── 📄 views.py             # Home page & health checks
│   │   └── 📄 urls.py              # Core URL patterns
│   ├── 📁 products/                # Product catalog
│   │   ├── 📁 api/                 # Product API endpoints
│   │   ├── 📄 models.py            # Product, Category, Review models
│   │   ├── 📄 views.py             # Product listing & detail views
│   │   └── 📄 admin.py             # Product admin interface
│   ├── 📁 orders/                  # Shopping cart & orders
│   │   ├── 📁 api/                 # Order API endpoints
│   │   ├── 📄 models.py            # Cart, Order, OrderItem models
│   │   ├── 📄 views.py             # Cart & checkout views
│   │   └── 📄 admin.py             # Order management
│   └── 📁 payments/                # Stripe payment processing
│       ├── 📁 api/                 # Payment API endpoints
│       ├── 📄 models.py            # Payment, Refund models
│       ├── 📄 views.py             # Payment processing views
│       └── 📄 admin.py             # Payment admin interface
├── 📁 ecommerce/                    # Main Django project
│   ├── 📄 settings.py              # Django configuration
│   ├── 📄 urls.py                  # Root URL routing
│   ├── 📄 wsgi.py                  # WSGI application
│   └── 📄 asgi.py                  # ASGI application
├── 📁 static/                      # Static assets
│   └── 📁 css/                     # Custom stylesheets
├── 📁 templates/                   # Django templates
│   ├── 📄 base.html                # Base template
│   ├── 📁 core/                    # Core app templates
│   ├── 📁 accounts/                # Authentication templates
│   └── 📁 products/                # Product templates
├── 📁 utils/                       # Utility modules
│   └── 📄 db.py                    # Database routing utilities
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env.example                 # Environment variables template
├── 📄 .gitignore                   # Git ignore rules
├── 📄 README.md                    # This file
└── 📄 manage.py                    # Django management script
```

## ⚙️ Configuration Guide

### Environment Variables Reference

#### Core Django Settings
| Variable | Description | Development | Production |
|----------|-------------|-------------|------------|
| `DEBUG` | Enable debug mode | `True` | `False` |
| `SECRET_KEY` | Django secret key | Any value | Strong secret |
| `ALLOWED_HOSTS` | Allowed hostnames | `localhost,127.0.0.1` | Your domains |

#### Database Configuration
| Variable | Description | Example |
|----------|-------------|---------|
| `PRIMARY_SQL_URL` | Write database URL | `postgresql://user:pass@host:5432/db` |
| `READ_SQL_URL` | Read replica URL | `postgresql://user:pass@replica:5432/db` |

#### Redis Cache
| Variable | Description | Example |
|----------|-------------|---------|
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/1` |
| `REDIS_SSL` | Use SSL for Redis | `False` (local), `True` (Azure) |

#### Azure Storage
| Variable | Description | Required |
|----------|-------------|----------|
| `USE_AZURE_STORAGE` | Enable Azure Blob Storage | Production |
| `AZURE_ACCOUNT_NAME` | Storage account name | Production |
| `AZURE_BLOB_KEY` | Storage access key | Production |
| `AZURE_CONTAINER` | Container name | Production |

#### Stripe Payment Processing
| Variable | Description | Get From |
|----------|-------------|----------|
| `STRIPE_PUBLISHABLE_KEY` | Public key for frontend | Stripe Dashboard |
| `STRIPE_SECRET_KEY` | Secret key for backend | Stripe Dashboard |
| `STRIPE_WEBHOOK_SECRET` | Webhook signature secret | Stripe Webhooks |

#### Azure B2C Authentication (Optional)
| Variable | Description |
|----------|-------------|
| `AZURE_B2C_TENANT_NAME` | B2C tenant name |
| `AZURE_B2C_CLIENT_ID` | Application client ID |
| `AZURE_B2C_CLIENT_SECRET` | Application secret |

#### Security Settings
| Variable | Description | Development | Production |
|----------|-------------|-------------|------------|
| `SECURE_SSL_REDIRECT` | Force HTTPS | `False` | `True` |
| `DJANGO_LOG_LEVEL` | Logging level | `DEBUG` | `INFO` |

### Database Architecture

The application supports sophisticated database routing:

- **Write Operations**: Routed to primary database
- **Read Operations**: Automatically routed to read replica
- **Migrations**: Only run on primary database
- **Failover**: Automatic fallback to primary if replica unavailable

```python
# Database router configuration in settings.py
DATABASE_ROUTERS = ["utils.db.ReadWriteRouter"]

# Supported operations
User.objects.all()  # → Read replica
User.objects.create()  # → Primary database
```

## ☁️ Azure Deployment Guide

### Required Azure Services

#### Core Infrastructure
1. **Azure App Service** (Linux, Python 3.9+)
   - Recommended: Premium v2 or v3 for production
   - Auto-scaling enabled
   - Multiple deployment slots for blue-green deployments

2. **Azure SQL Database** (Business Critical tier)
   - Active geo-replication enabled
   - Automatic failover groups
   - Point-in-time restore configured

3. **Azure Cache for Redis** (Enterprise tier)
   - Active geo-replication
   - High availability with zone redundancy
   - Data persistence enabled

4. **Azure Blob Storage** (Standard RA-GRS)
   - Cross-region replication
   - CDN integration
   - Private endpoints

5. **Azure Front Door Premium**
   - Web Application Firewall (WAF)
   - Global load balancing
   - DDoS protection

6. **Azure Key Vault**
   - Secrets management
   - SSL certificates storage
   - Managed identity integration

#### Monitoring & Security
7. **Application Insights**
8. **Log Analytics Workspace**
9. **Azure Monitor**
10. **Azure Private DNS**

### Step-by-Step Deployment

#### Phase 1: Resource Provisioning

```bash
# Login to Azure
az login

# Create resource group
az group create --name ecommerce-prod-rg --location eastus

# Deploy infrastructure using ARM template or Bicep
az deployment group create \
  --resource-group ecommerce-prod-rg \
  --template-file azure-resources.json \
  --parameters @parameters.json
```

#### Phase 2: App Service Configuration

```bash
# Create App Service Plan
az appservice plan create \
  --name ecommerce-plan \
  --resource-group ecommerce-prod-rg \
  --sku P2V2 \
  --is-linux

# Create Web App
az webapp create \
  --resource-group ecommerce-prod-rg \
  --plan ecommerce-plan \
  --name your-ecommerce-app \
  --runtime "PYTHON|3.9"

# Configure application settings
az webapp config appsettings set \
  --resource-group ecommerce-prod-rg \
  --name your-ecommerce-app \
  --settings @app-settings.json
```

#### Phase 3: Database Setup

```bash
# Run migrations via App Service console or SSH
az webapp ssh --resource-group ecommerce-prod-rg --name your-ecommerce-app

# In the SSH session:
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

#### Phase 4: CI/CD Pipeline

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Azure App Service

on:
  push:
    branches: [ main ]

env:
  AZURE_WEBAPP_NAME: your-ecommerce-app
  PYTHON_VERSION: '3.9'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Run tests
      run: python manage.py test
      
    - name: Deploy to Azure Web App
      uses: azure/webapps-deploy@v2
      with:
        app-name: ${{ env.AZURE_WEBAPP_NAME }}
        publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
```

### Production Configuration Checklist

#### Security
- [ ] SSL/TLS certificates configured
- [ ] WAF rules implemented
- [ ] Private endpoints enabled
- [ ] Managed identity configured
- [ ] Key Vault integration active
- [ ] Network security groups configured

#### Performance
- [ ] Auto-scaling rules set
- [ ] CDN configured for static files
- [ ] Database connection pooling
- [ ] Redis cache warming
- [ ] Application Insights configured

#### Reliability
- [ ] Health check endpoints configured
- [ ] Backup strategies implemented
- [ ] Disaster recovery tested
- [ ] Monitoring alerts configured
- [ ] Log aggregation setup

## 🔌 API Documentation

### RESTful API Endpoints

#### Products API
```http
GET /api/v1/products/                    # List all products with pagination
GET /api/v1/products/{id}/               # Get product details
GET /api/v1/products/featured/           # Get featured products
GET /api/v1/products/search/?q=term      # Search products
GET /api/v1/categories/                  # List categories
GET /api/v1/categories/{id}/products/    # Products in category
```

#### Orders & Cart API
```http
GET /api/v1/orders/                      # List user orders
GET /api/v1/orders/{id}/                 # Get order details
GET /api/v1/cart/                        # Get user cart
POST /api/v1/cart/add_item/              # Add item to cart
PATCH /api/v1/cart/update_item/          # Update cart item
DELETE /api/v1/cart/remove_item/         # Remove cart item
DELETE /api/v1/cart/clear/               # Clear entire cart
```

#### Payments API
```http
GET /api/v1/payments/                    # List user payments
POST /api/v1/payments/create-intent/     # Create Stripe PaymentIntent
POST /api/v1/payments/confirm/           # Confirm payment
GET /api/v1/payments/payment_methods/    # User's saved payment methods
```

### API Authentication

```bash
# Session-based authentication for web app
curl -H "Cookie: sessionid=<session_id>" \
     http://localhost:8000/api/v1/products/

# API responses include pagination
{
  "count": 150,
  "next": "http://localhost:8000/api/v1/products/?page=2",
  "previous": null,
  "results": [...]
}
```

## 🔒 Security Features

### Application Security
- ✅ **Content Security Policy** (CSP) headers with nonce support
- ✅ **HTTPS enforcement** with HSTS headers
- ✅ **Rate limiting** on authentication endpoints (django-axes)
- ✅ **SQL injection protection** via Django ORM
- ✅ **XSS protection** via template escaping and CSP
- ✅ **CSRF protection** on all forms with SameSite cookies
- ✅ **Secure session handling** with HttpOnly and Secure flags

### Infrastructure Security
- ✅ **Private endpoints** for all Azure services
- ✅ **Web Application Firewall** via Azure Front Door Premium
- ✅ **DDoS protection** on virtual networks
- ✅ **Network Security Groups** with deny-by-default rules
- ✅ **Managed Identity** for service-to-service authentication
- ✅ **Key Vault integration** for secrets management

### Data Protection
- ✅ **Encryption at rest** for databases and storage
- ✅ **Encryption in transit** with TLS 1.2+
- ✅ **Data masking** in non-production environments
- ✅ **Automated backups** with point-in-time recovery
- ✅ **Access logging** for audit compliance

## 📊 Monitoring and Observability

### Application Performance Monitoring

```python
# Built-in health check endpoint
GET /health/
{
  "status": "healthy",
  "database": "connected",
  "cache": "connected",
  "storage": "available"
}
```

### Key Metrics Tracked
- 🎯 **Apdex scores** for user experience
- ⚡ **Response times** (P50, P95, P99)
- 🚨 **Error rates** by endpoint and status code
- 💳 **Payment success rates** and failure reasons
- 🛒 **Conversion funnel** metrics
- 👥 **Active user sessions**
- 💾 **Database performance** and connection pooling

### Alerting Strategy
- 📈 **SLO-based alerting** for critical user journeys
- 🔥 **Error budget burn** rate monitoring
- 💔 **Failed payment** immediate notifications
- 🐌 **Performance degradation** early warnings
- 🔒 **Security incident** automated responses

### Log Management
```python
# Structured logging with correlation IDs
import logging
import uuid

logger = logging.getLogger(__name__)

def process_order(request, order_id):
    correlation_id = str(uuid.uuid4())
    logger.info(
        "Processing order",
        extra={
            "correlation_id": correlation_id,
            "order_id": order_id,
            "user_id": request.user.id
        }
    )
```

## 🚀 Advanced Features

### Stripe Payment Processing
- 💳 **Multiple Payment Methods**: Cards, wallets, bank transfers
- 🔐 **3D Secure Authentication**: SCA compliance for European customers  
- 💰 **Saved Payment Methods**: Secure tokenization for returning customers
- 🔄 **Webhook Processing**: Real-time payment status updates
- 💸 **Refund Management**: Full and partial refund capabilities
- 📊 **Payment Analytics**: Transaction reporting and insights

### Global Performance Architecture
```mermaid
graph TD
    A[Azure Front Door] --> B[App Service US East]
    A --> C[App Service Europe West]
    B --> D[SQL Database Primary]
    C --> E[SQL Database Replica]
    B --> F[Redis Enterprise]
    C --> F
    B --> G[Blob Storage RA-GRS]
    C --> G
```

### E-commerce Features
- 🛍️ **Product Variants**: Size, color, style options
- ⭐ **Review System**: Customer feedback and ratings
- 📦 **Inventory Management**: Real-time stock tracking
- 🚚 **Order Fulfillment**: Status tracking and notifications
- 🎯 **Personalization**: Recommendation engine ready
- 📱 **Mobile Responsive**: PWA capabilities

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Development Process
1. 🍴 **Fork** the repository
2. 🌟 **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. ✅ **Test** your changes: `python manage.py test`
4. 📝 **Commit** with clear messages: `git commit -m 'Add payment refund API'`
5. 🚀 **Push** to your branch: `git push origin feature/amazing-feature`
6. 🔄 **Open** a Pull Request

### Code Standards
- Follow **PEP 8** style guidelines
- Add **docstrings** to all functions and classes
- Include **unit tests** for new features
- Update **documentation** as needed
- Use **type hints** where appropriate

### Testing Requirements
```bash
# All tests must pass
python manage.py test

# Code coverage should be > 80%
coverage run --source='.' manage.py test
coverage report --fail-under=80

# No security vulnerabilities
pip install safety
safety check
```

## 📋 Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check database connectivity
python manage.py dbshell

# Reset database connections
python manage.py shell
>>> from django.db import connection
>>> connection.close()
```

#### Stripe Integration Issues
```bash
# Test Stripe connection
python manage.py shell
>>> import stripe
>>> stripe.api_key = 'sk_test_...'
>>> stripe.Account.retrieve()
```

#### Azure Storage Problems
```bash
# Verify Azure credentials
python manage.py shell
>>> from django.core.files.storage import default_storage
>>> default_storage.exists('test.txt')
```

### Getting Help
- 📚 **Documentation**: Check this README and inline code comments
- 🐛 **Bug Reports**: Open an issue with reproduction steps
- 💡 **Feature Requests**: Use issue templates for new ideas  
- 💬 **Questions**: Start a discussion in GitHub Discussions
- 🆘 **Urgent Issues**: Contact maintainers directly

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🏢 Enterprise Support

For enterprise deployments, we offer:
- 🔧 **Custom Integration** services
- 🏗️ **Architecture Consulting**
- 🎓 **Training Programs**
- 🛡️ **Security Audits**
- ⚡ **Performance Optimization**

Contact us for enterprise pricing and support options.

---

<div align="center">

**Made with ❤️ for the Django and Azure community**

[![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://djangoproject.com/)
[![Azure](https://img.shields.io/badge/Azure-Cloud-blue.svg)](https://azure.microsoft.com/)
[![Stripe](https://img.shields.io/badge/Stripe-Payments-blueviolet.svg)](https://stripe.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-yellow.svg)](https://python.org/)

[⭐ Star this repo](https://github.com/aaronbui99/Azure-Ecommerce-Django-Stripe) • [🐛 Report Bug](https://github.com/aaronbui99/Azure-Ecommerce-Django-Stripe/issues) • [✨ Request Feature](https://github.com/aaronbui99/Azure-Ecommerce-Django-Stripe/issues)

</div>

## This project belongs to Bui Thanh Huy (Aaron Bui)
- Email: aaronhuy2509@gmail.com
- Linkedin: https://www.linkedin.com/in/huy-bui-thanh-372a56194/