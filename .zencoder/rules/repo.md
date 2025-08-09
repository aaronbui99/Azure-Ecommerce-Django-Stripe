---
description: Repository Information Overview
alwaysApply: true
---

# Azure E-commerce Django Stripe Information

## Summary
A Django-based e-commerce platform designed for global deployment on Azure with Stripe integration. The architecture follows a "Monolith-first" approach with Active-Active configuration for global low-latency with minimal operations overhead.

## Structure
The project follows a standard Django application structure with additional components for Azure integration, payment processing, and global distribution.

## Language & Runtime
**Language**: Python
**Framework**: Django
**Build System**: Standard Python build tools
**Package Manager**: pip

## Dependencies
**Main Dependencies**:
- Django - Web framework
- django-redis - Redis cache backend
- django-storages[azure] - Azure Blob Storage integration
- django-environ - Environment variable management
- django-axes - Rate limiting for authentication
- django-csp - Content Security Policy
- psycopg2-binary - PostgreSQL adapter

**Azure Services**:
- Azure App Service (Linux, container or Python runtime)
- Azure Front Door (Premium) with WAF
- Azure SQL Database (Business Critical)
- Azure Cache for Redis Enterprise
- Azure Blob Storage
- Azure AI Search
- Azure Functions
- Azure Event Grid
- Azure Key Vault
- Microsoft Entra ID B2C

## Database Configuration
**Primary Database**: Azure SQL Database with active geo-replication
```python
DATABASES = {
    "default": dj_database_url.parse(os.getenv("PRIMARY_SQL_URL")),
    "replica": dj_database_url.parse(os.getenv("READ_SQL_URL")),
}
DATABASE_ROUTERS = ["utils.db.ReadWriteRouter"]  # route SELECTs to replica
```

## Caching & Sessions
**Cache System**: Azure Cache for Redis Enterprise with Active-Geo Replication
```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "rediss://<redis-name>.redis.cache.windows.net:6380/0",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient", "SSL": True},
        "TIMEOUT": 300,
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
```

## Storage Configuration
**Storage System**: Azure Blob Storage with RA-GRS
```python
INSTALLED_APPS += ["storages"]
AZURE_ACCOUNT_NAME = "mystore"
AZURE_ACCOUNT_KEY = os.getenv("AZURE_BLOB_KEY")
DEFAULT_FILE_STORAGE = "storages.backends.azure_storage.AzureStorage"
```

## Security
**Authentication**: Microsoft Entra ID B2C for customer auth
**Security Features**:
- Private Endpoints for SQL/Blob/Search/Redis
- Key Vault for secrets
- WAF on Front Door
- DDoS protection on vNet
- NSG "deny by default" + explicit allowlists (SSRF protection)
- django-axes for rate limiting authentication
- django-csp for Content Security Policy
- SECURE_* settings (HSTS, cookies Secure & HttpOnly, REFERRER_POLICY)

## Deployment Architecture
**Primary Architecture**: PaaS "Monolith-first", Active-Active
**Compute**: Azure App Service (one app per region)
**Global Entry**: Azure Front Door with WAF, health probes, and routing
**Async Jobs**: Azure Functions for emails, order confirmations, thumbnails
**Events**: Event Grid for order-created events

## Alternative Architectures
1. **Containerized "Service-oriented"**:
   - Azure Container Apps or AKS
   - Split databases per bounded context
   - Azure Service Bus for queues

2. **Global "Read-local / Write-primary" with Postgres**:
   - Azure Database for PostgreSQL Flexible Server
   - Geo-read replicas per region

3. **High-scale Catalog with Multi-Master**:
   - Azure Cosmos DB with multi-region write
   - Single-writer RDBMS for orders/payments

## Observability
**Monitoring**: App Insights + Log Analytics + Front Door logs
**Features**:
- Per-region dashboards
- SLOs monitoring
- Synthetic checks per region
- Alerting on Apdex, p95 latency, error budget burn
- Business KPIs as first-class alerts

## CI/CD & Infrastructure as Code
**CI/CD**: GitHub Actions for build, test, security scan, container scan, infrastructure deployment
**Deployment Strategy**: Blue/green or canary via Front Door weight split
**Database Migrations**: GitHub Actions job gated by manual approval

## Resilience & Disaster Recovery
**App Tier**: Active-Active configuration
**Database**: RPO/RTO via geo-replication + automated backups
**Testing**: Chaos tests including region failover drills

## Rollout Roadmap
1. **MVP (1 region)**: App Service + Azure SQL + Redis + Blob + Front Door + App Insights
2. **Multi-region**: Clone stack to 2nd region with Front Door anycast + health probes
3. **Hardening**: Private Endpoints, WAF rules, egress allowlists, Key Vault, Managed Identity
4. **Scale out**: Split reads to replicas, add Service Bus + Functions, add AI Search
5. **Advanced**: Containerize hot paths, introduce per-service canary, consider Cosmos DB