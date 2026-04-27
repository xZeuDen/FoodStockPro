# FoodStockPro

## Description
FoodStockPro is a Django web application for restaurant inventory and purchase order management. It helps a food business track ingredients, manage supplier purchase orders, record stock movements, and handle kitchen ingredient requests.

## Module Context
This project was created for a Web Framework Development module.

## Theme
Food / restaurant stock management.

## Must-Have Use Case
Purchase Orders with Purchase Order Items.

## Main Roles
- Manager
- Kitchen Staff
- Supplier
- Finance Officer

## Main Features
- User registration, login, logout, profiles, and role-based dashboards.
- Ingredient categories, ingredients, stock levels, and stock movement history.
- Supplier records.
- Purchase orders with purchase order items.
- Automatic stock increase when a purchase order is marked as delivered.
- Kitchen ingredient requests.
- Manager approval, rejection, and fulfilment workflow for kitchen requests.
- Supplier purchase order status updates.
- Basic automated tests for models, pages, and workflows.

## Technologies Used
- Python
- Django
- SQLite
- HTML
- CSS
- Bootstrap via CDN

## How To Run Locally
From the project folder:

```bash
python manage.py runserver
```

Then open the local development server URL shown in the terminal.

## How To Run Migrations
Create migration files:

```bash
python manage.py makemigrations
```

Apply migrations:

```bash
python manage.py migrate
```

## How To Load Fixtures
Fixtures can be loaded with Django's `loaddata` command, for example:

```bash
python manage.py loaddata users.json
```

Sample data can also be generated with:

```bash
python manage.py seed_foodstockpro
```

After generating sample data, it can be exported later using Django's `dumpdata` command.

## Test Users
All sample users use the password `password`.

- `admin / password`
- `manager1 / password`
- `kitchen1 / password`
- `supplier1 / password`
- `finance1 / password`

## How To Run Tests
Run:

```bash
python manage.py test
```

At the time of writing, 20 automated tests pass.

## Deployment
Deployment has not been completed for this project yet.
