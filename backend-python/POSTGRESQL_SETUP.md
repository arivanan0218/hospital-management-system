# PostgreSQL Setup Guide

This guide helps you connect your Hospital Management System to PostgreSQL database instead of using JSON files.

## Prerequisites

### 1. Install PostgreSQL

#### Windows
1. Download PostgreSQL from [https://www.postgresql.org/download/windows/](https://www.postgresql.org/download/windows/)
2. Run the installer with default settings
3. Remember the password you set for the `postgres` user
4. Add PostgreSQL bin directory to your PATH environment variable

#### macOS
```bash
# Using Homebrew
brew install postgresql
brew services start postgresql
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Create Database User (Optional)
```sql
-- Connect to PostgreSQL as postgres user
psql -U postgres

-- Create a new user for your application
CREATE USER hospital_user WITH PASSWORD 'your_password';

-- Create database
CREATE DATABASE hospital_management OWNER hospital_user;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE hospital_management TO hospital_user;
```

## Quick Setup

### 1. Install Dependencies
```bash
cd backend-python
pip install -e .
```

### 2. Configure Environment
Update the `.env` file with your PostgreSQL credentials:

```env
# PostgreSQL Database Configuration
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/hospital_management
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hospital_management
DB_USER=postgres
DB_PASSWORD=your_password
```

### 3. Run Automated Setup
```bash
python setup_postgresql.py
```

This script will:
- Install required dependencies
- Check PostgreSQL installation
- Create the database
- Set up tables
- Migrate existing JSON data to PostgreSQL

### 4. Test Connection
```bash
python database.py
```

## Manual Setup

If you prefer manual setup:

### 1. Create Database
```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE hospital_management;

-- Switch to the database
\c hospital_management;
```

### 2. Set up Tables
```bash
python -c "from database import create_tables; create_tables()"
```

### 3. Migrate Data
```bash
python -c "from database import migrate_json_to_db; migrate_json_to_db()"
```

## Features

### Automatic Fallback
The system automatically falls back to JSON files if:
- PostgreSQL is not available
- Database connection fails
- Dependencies are not installed

### Database Operations
- **CREATE**: Add new users to PostgreSQL
- **READ**: Query users from PostgreSQL
- **UPDATE**: Modify existing user records
- **DELETE**: Remove users from database

### Benefits of PostgreSQL
1. **Performance**: Much faster than JSON for large datasets
2. **Concurrency**: Multiple users can access simultaneously
3. **ACID Compliance**: Data integrity guaranteed
4. **Scalability**: Can handle millions of records
5. **Security**: Built-in user authentication and permissions
6. **Backup**: Easy database backup and restore

## Troubleshooting

### Connection Errors
```bash
# Test PostgreSQL service
pg_isready -U postgres

# Check if database exists
psql -U postgres -l | grep hospital_management

# Test connection with credentials
psql -U postgres -d hospital_management -c "SELECT 1;"
```

### Permission Issues
```sql
-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE hospital_management TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
```

### Port Conflicts
If PostgreSQL is running on a different port:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5433/hospital_management
DB_PORT=5433
```

## Development vs Production

### Development
- Use SQLite for local development: `sqlite:///./hospital.db`
- Simple setup, no external dependencies
- Perfect for testing and development

### Production
- Use PostgreSQL for production deployments
- Better performance and reliability
- Supports multiple concurrent users

## Migration Commands

### Export data from PostgreSQL to JSON
```python
from database import SessionLocal, User as DBUser
import json

db = SessionLocal()
users = db.query(DBUser).all()
user_data = [{"id": u.id, "name": u.name, "email": u.email, "address": u.address, "phone": u.phone} for u in users]

with open("backup_users.json", "w") as f:
    json.dump(user_data, f, indent=2)
```

### Import data from JSON to PostgreSQL
```python
from database import migrate_json_to_db
migrate_json_to_db()
```

## Next Steps

1. **Frontend Integration**: Update frontend to work with the new database endpoints
2. **Authentication**: Add user authentication and authorization
3. **Backup Strategy**: Set up regular database backups
4. **Monitoring**: Add database performance monitoring
5. **Scaling**: Consider connection pooling for high-traffic applications
