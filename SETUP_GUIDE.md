# BioPellet Trade - Setup Guide

This guide provides instructions for setting up and running the Biomass Pellet Trading Platform locally.

## Table of Contents
- [Method 1: Docker Setup (Recommended)](#method-1-docker-setup-recommended)
- [Method 2: Manual Setup](#method-2-manual-setup)
- [Features Overview](#features-overview)
- [User Roles](#user-roles)
- [Database Schema](#database-schema)
- [Troubleshooting](#troubleshooting)

## Method 1: Docker Setup (Recommended)

The easiest way to run the application is using Docker and Docker Compose, which handles all dependencies and database setup automatically.

### Requirements
- Docker
- Docker Compose

### Steps

1. **Clone the repository**

```bash
git clone <repository-url>
cd <repository-directory>
```

2. **Build and start the containers**

```bash
docker-compose up -d
```

3. **Initialize the database**

```bash
# Connect to the web container
docker-compose exec web bash

# Initialize the database
python -c "from app import app, db; \
           with app.app_context(): \
           db.create_all()"
exit
```

4. **Access the application**

Open your browser and navigate to:
```
http://localhost:5000
```

5. **Stopping the application**

```bash
docker-compose down
```

## Method 2: Manual Setup

### Requirements
- Python 3.8 or higher
- PostgreSQL database (optional - you can use SQLite for local development)

### Installation Steps

1. **Clone the repository**

```bash
git clone <repository-url>
cd <repository-directory>
```

2. **Create a virtual environment**

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements-local.txt
```

4. **Set up environment variables**

Create a `.env` file in the root directory with the following variables:

```
# For PostgreSQL
DATABASE_URL=postgresql://username:password@localhost:5432/biopellet_trade

# Or for SQLite (easier for local testing)
# DATABASE_URL=sqlite:///pellet_trading.db

# Secret key for session
SESSION_SECRET=your_secret_key_here
```

5. **Initialize the database**

```bash
# Open a Python shell
python

# In the Python shell
from app import app, db
with app.app_context():
    db.create_all()
exit()
```

6. **Run the application**

```bash
# Development mode
python main.py

# Or with Gunicorn (production)
gunicorn --bind 0.0.0.0:5000 main:app
```

7. **Access the application**

Open your web browser and navigate to:
```
http://localhost:5000
```

## Features Overview

- Landing page accessible without login
- User registration and login system
- Role-based access (Farmer and Company)
- Farmer dashboard for listing and selling pellets
- Company dashboard for browsing and purchasing pellets
- Offer and order management system

## User Roles

- **Farmers**: Can list pellets for sale, respond to offers, and manage orders
- **Companies**: Can browse available pellets, post requirements, make offers, and place orders

## Database Schema

The application uses the following main models:
- User (with Farmer and Company profiles)
- PelletListing
- Requirement
- Offer
- Order

## Troubleshooting

- If you encounter database connection errors, check your DATABASE_URL and ensure your PostgreSQL server is running
- For "module not found" errors, make sure all dependencies are installed correctly
- For permission errors, ensure you have write access to the directory for SQLite or correct privileges for PostgreSQL
- If using Docker, ensure Docker and Docker Compose are correctly installed and running