# 🌱 DZ-Fellah - Algerian Farm-to-Consumer Marketplace

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0-green.svg)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

A comprehensive marketplace platform connecting Algerian farmers (producers) with consumers. Built with Django REST Framework and PostgreSQL, featuring a raw SQL approach for optimized database queries.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
  - [Local Development](#local-development)
  - [Docker Development](#docker-development)
- [Database Setup](#-database-setup)
- [Demo Data](#-demo-data)
- [Testing](#-testing)
- [Available Commands](#-available-commands)

---

## ✨ Features

### 🎯 Core Features
- **Dual User Types**: Producers (farmers) and Clients (consumers)
- **JWT Authentication**: Secure token-based authentication
- **Product Management**: Full CRUD operations for products
- **Shopping Cart**: Session-based cart with real-time validation
- **Order System**: Multi-producer order management with sub-orders
- **Anti-Gaspi System**: Automatic discount system for products nearing expiration

### 🛒 Shopping & Orders
- Add products to cart with stock validation
- Create orders from cart (automatically splits by producer)
- Track order status (pending → confirmed → preparing → ready → completed)
- Producer-specific sub-orders for efficient fulfillment
- Quantity adjustments for weight-based products

### 🔍 Search & Filter
- Search products by name/description
- Filter by type, price range, location (wilaya)
- Anti-gaspi product listings
- Producer shop pages

### 👨‍🌾 Producer Features
- Create and manage products
- View and manage incoming orders
- Update order status
- Adjust quantities for weight-based products
- Bio certification badge

---

## 🛠 Tech Stack

- **Backend**: Django 6.0, Django REST Framework
- **Database**: PostgreSQL 15
- **Authentication**: JWT (djangorestframework-simplejwt)
- **API**: RESTful architecture
- **Testing**: Pytest, pytest-django
- **Containerization**: Docker, Docker Compose

### Key Design Choices
- **Raw SQL Queries**: Optimized database access with custom query layer
- **No Django ORM Models**: Direct SQL for better performance control
- **Custom Authentication**: JWT-based with custom user object
- **Role-Based Permissions**: Producer and Client specific permissions

---

## 📁 Project Structure

```
dzfellah/
├── cart/                   # Shopping cart functionality
│   ├── models.py          # Cart and CartItem models
│   ├── serializers.py     # Cart serializers
│   ├── views.py           # Cart API endpoints
│   └── urls.py
├── config/                 # Django project settings
│   ├── settings.py        # Main settings
│   ├── urls.py            # Root URL configuration
│   └── management/
│       └── commands/
│           ├── setup_db.py       # Database schema setup
│           ├── create_demo_data.py  # Demo data creation
│           └── clear_demo_data.py   # Clear all data
├── db/                     # Database layer
│   ├── schemas/           # SQL schema files
│   │   ├── 01_schema_users.sql
│   │   ├── 02_schema_products.sql
│   │   ├── 03_schema_cart.sql
│   │   └── 04_schema_orders.sql
│   ├── connection.py      # Database connection utilities
│   ├── users_queries.py   # User-related SQL queries
│   └── products_queries.py # Product-related SQL queries
├── order/                  # Order management
│   ├── models.py          # Order, SubOrder, OrderItem models
│   ├── serializers.py     # Order serializers
│   ├── views.py           # Order API endpoints
│   └── urls.py
├── products/               # Product management
│   ├── queries.py         # Product SQL queries
│   ├── serializers.py     # Product serializers
│   ├── views.py           # Product API endpoints
│   └── urls.py
├── users/                  # User management & auth
│   ├── queries.py         # User SQL queries
│   ├── serializers.py     # User serializers
│   ├── views.py           # Auth & user endpoints
│   ├── authentication.py  # Custom JWT authentication
│   ├── permissions.py     # Custom permissions
│   └── urls.py
├── tests/                  # Test suite
│   └── test_queries.py    # Query layer tests
├── docker-compose.yaml     # Docker orchestration
├── Dockerfile             # Docker image definition
├── requirements.txt       # Python dependencies
├── pytest.ini            # Pytest configuration
└── manage.py             # Django management script
```

---

## 📦 Prerequisites

### Local Development
- Python 3.12+
- PostgreSQL 15+
- pip (Python package manager)

### Docker Development
- Docker 20.10+
- Docker Compose 2.0+

---

## 🚀 Installation

### Local Development

#### 1. Clone the repository
```bash
git clone https://github.com/yourusername/dzfellah.git
cd dzfellah
```

#### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install dependencies
```bash
pip install -r requirements.txt
```

#### 4. Create PostgreSQL database
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE dzfellah;
\q
```

---

### Docker Development

#### 1. Clone the repository
```bash
git clone https://github.com/yourusername/dzfellah.git
cd dzfellah
```

#### 2. Build and start containers
```bash
docker-compose up -d
```

This will:
- Create PostgreSQL container
- Create Django app container
- Set up networking between containers
- Run migrations automatically

---

## 🗄️ Database Setup

### Create Database Schema

After installation, set up the database tables:

```bash
# Local development
python manage.py setup_db

# Docker
docker-compose exec web python manage.py setup_db
```

This command will:
- Execute all SQL files in `db/schemas/` directory
- Create users, producers, clients, products, carts, and orders tables
- Set up indexes and constraints
- Create triggers for `updated_at` fields

#### Expected Output:
```
📁 Found 4 SQL file(s) to execute:
   • 01_schema_users.sql
   • 02_schema_products.sql
   • 03_schema_cart.sql
   • 04_schema_orders.sql

============================================================
🔄 Executing 01_schema_users.sql...
   ✓ Successfully executed 01_schema_users.sql
🔄 Executing 02_schema_products.sql...
   ✓ Successfully executed 02_schema_products.sql
...
============================================================
✓ Success: 4 file(s)
🎉 All schema files executed successfully!
```

---

## 🌾 Demo Data

### Create Demo Data

Populate the database with realistic demo data:

```bash
# Local development
python manage.py create_demo_data

# Docker
docker-compose exec web python manage.py create_demo_data
```

This will create:
- **5 Producer accounts** with different profiles:
  - Ferme Bio Alger (Bio certified, vegetables)
  - Les Jardins d'Oran (Fruits & vegetables)
  - Miel & Nature Tlemcen (Honey products)
  - Ferme des Oliviers (Olive oil & olives)
  - Jardin de la Mitidja (Citrus fruits)

- **3 Client accounts** for testing purchases

- **25+ Products** across different categories:
  - Fresh vegetables (tomatoes, carrots, lettuce)
  - Fruits (oranges, apples, strawberries)
  - Processed products (honey, olive oil)
  - Anti-gaspi products (discounted items)

---

### Authentication
Most endpoints require JWT authentication. Include the token in headers:
```
Authorization: Bearer <your_access_token>
```

### Main Endpoints

#### Authentication
```
POST /api/auth/register/producer/  # Register as producer
POST /api/auth/register/client/    # Register as client
POST /api/auth/login/               # Login
POST /api/auth/logout/              # Logout
```

#### Users
```
GET /api/users/me/                  # Get current user profile
```

#### Products (Public)
```
GET  /api/products/                 # List products (random order)
GET  /api/products/{id}/            # Get product detail
GET  /api/products/search/?q=...    # Search products
GET  /api/products/filter/          # Filter products
GET  /api/products/producer/{id}/   # Get producer's shop
```

#### Products (Producer Only)
```
GET    /api/my-products/            # List my products
POST   /api/my-products/            # Create product
GET    /api/my-products/{id}/       # Get my product detail
PUT    /api/my-products/{id}/       # Update product
PATCH  /api/my-products/{id}/       # Partial update
DELETE /api/my-products/{id}/       # Delete product
POST   /api/my-products/{id}/toggle-anti-gaspi/  # Toggle anti-gaspi
```

#### Shopping Cart (Client)
```
GET    /api/cart/my_cart/           # Get my cart
POST   /api/cart/add_item/          # Add item to cart
PATCH  /api/cart/update_item/{id}/  # Update item quantity
DELETE /api/cart/remove_item/{id}/  # Remove item
DELETE /api/cart/clear_cart/        # Clear cart
GET    /api/cart/validate_cart/     # Validate cart before checkout
```

#### Orders (Client)
```
POST   /api/orders/create_from_cart/  # Create order from cart
GET    /api/orders/my_orders/         # List my orders
GET    /api/orders/{id}/              # Get order detail
POST   /api/orders/{id}/cancel/       # Cancel order
```

#### Producer Orders
```
GET   /api/producer-orders/my_orders/           # List my sub-orders
GET   /api/producer-orders/{id}/                # Get sub-order detail
PATCH /api/producer-orders/{id}/update_status/  # Update status
PATCH /api/producer-orders/{id}/adjust_item/{item_id}/  # Adjust quantity
```

### Swagger Documentation
View full API documentation:
```
swagger.yaml - Complete API documentation
swagger_cart_order.yaml - Cart & Order API documentation
```

---

## 🧪 Testing

### Run Tests

```bash
# Local development
pytest

# With coverage
pytest --cov=users --cov=products --cov-report=html

# Docker
docker-compose exec web pytest
```

### Test Structure
```
tests/
└── test_queries.py
    ├── TestUserQueries      # User CRUD operations
    ├── TestProductQueries   # Product CRUD operations
    └── TestIntegration      # End-to-end workflows
```

---

## 📝 Available Commands

### Django Management Commands

```bash
# Run development server
python manage.py runserver

# Create database schema
python manage.py setup_db

# Create demo data
python manage.py create_demo_data

# Clear all data
python manage.py clear_demo_data --yes

# Run migrations (Django models)
python manage.py migrate

# Create superuser (for Django admin)
python manage.py createsuperuser

# Run tests
pytest
```

### Docker Commands

```bash
# Start containers
docker-compose up -d

# Stop containers
docker-compose down

# View logs
docker-compose logs -f

# Execute command in container
docker-compose exec web python manage.py <command>

# Rebuild containers
docker-compose up -d --build

# Access PostgreSQL
docker-compose exec db psql -U postgres -d dzfellah
```

---

## 🚀 Quick Start Guide

### 1. Docker Setup (Recommended)

```bash
# Clone repository
git clone https://github.com/yourusername/dzfellah.git
cd dzfellah

# Start containers
docker-compose up -d

# Create database schema
docker-compose exec web python manage.py setup_db

# Create demo data
docker-compose exec web python manage.py create_demo_data

# API is ready at http://localhost:8000/api
```

### 2. Test the API

```bash
# Login as client
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "client1@example.com",
    "password": "Client123"
  }'

# Get products (no auth required)
curl http://localhost:8000/api/products/

# Add to cart (use token from login)
curl -X POST http://localhost:8000/api/cart/add_item/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'
```

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 👥 Authors

- **Iyad SEBTI** - 

---

## 🙏 Acknowledgments

- Django REST Framework documentation
- PostgreSQL community
- Algerian agricultural community

---

## 📞 Support

For support, email i_sebti@estin.dz or open an issue on GitHub.

---

**Made with ❤️ for Algerian farmers and consumers**
