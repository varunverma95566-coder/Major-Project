# Production Database Integration Guide

The only remaining integration required for full production deployment is supplying connection credentials for your enterprise database instance.

## 1. Architectural Separation

All database queries are encapsulated inside repository abstractions (`app/repositories/base.py`, `dataset_repo.py`, `alert_repo.py`, etc.). Application routers and ML services never make direct raw SQL or engine-specific calls.

## 2. Steps to Connect Your Database

### Step 1: Install Enterprise Database Drivers (If not already installed)
For PostgreSQL:
```bash
pip install psycopg2-binary
```
For MySQL:
```bash
pip install pymysql
```

### Step 2: Configure Environment Variable in `.env`
Update the `DATABASE_URL` entry in `.env` located at the project root:
```env
# PostgreSQL Example:
DATABASE_URL=postgresql+psycopg2://db_user:SecurePassword123@localhost:5432/nids_enterprise_db

# MySQL Example:
# DATABASE_URL=mysql+pymysql://db_user:SecurePassword123@localhost:3306/nids_enterprise_db
```

### Step 3: Run Database Migrations
Apply the complete database schema via Alembic:
```bash
cd backend
alembic upgrade head
```

### Step 4: Seed Initial Knowledge Bases (Optional)
Populate standard MITRE ATT&CK techniques, demo users, and federated client records:
```bash
python -m app.seed.seeder
```

The application is now fully running against your live database instance without a single line of application code changed.
