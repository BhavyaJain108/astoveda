# PostgreSQL Setup for Production

## Install PostgreSQL

### macOS (using Homebrew):
```bash
brew install postgresql
brew services start postgresql
```

### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

## Create Database and User

```bash
# Connect to PostgreSQL as superuser
sudo -u postgres psql

# Create database
CREATE DATABASE astoveda_quiz;

# Create user with password
CREATE USER quiz_user WITH PASSWORD 'your_secure_password_here';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE astoveda_quiz TO quiz_user;

# Exit PostgreSQL
\q
```

## Update Environment Variables

Update your `.env` file:

```bash
# Change from SQLite to PostgreSQL
DATABASE_URL=postgresql://quiz_user:your_secure_password_here@localhost:5432/astoveda_quiz

# Generate secure keys
SECRET_KEY=your-very-secure-secret-key-here
ENCRYPTION_KEY=your-32-byte-encryption-key-here
ADMIN_PASSWORD=your-secure-admin-password
```

## Initialize Database with Migrations

```bash
# Install dependencies
pip install -r requirements.txt

# Run migration setup
python migrations_setup.py

# Or manually:
# flask db init
# flask db migrate -m "Initial migration"
# flask db upgrade
```

## Security Checklist

- [ ] Change default admin password
- [ ] Generate secure SECRET_KEY (use `python -c "import secrets; print(secrets.token_hex(32))"`)
- [ ] Generate secure ENCRYPTION_KEY (32 bytes)
- [ ] Use SSL/TLS in production
- [ ] Regular database backups
- [ ] Monitor for suspicious activity
- [ ] Limit database user permissions
- [ ] Use connection pooling
- [ ] Enable query logging for monitoring

## Backup Strategy

```bash
# Daily backup script
pg_dump -h localhost -U quiz_user -d astoveda_quiz > backup_$(date +%Y%m%d).sql

# Restore from backup
psql -h localhost -U quiz_user -d astoveda_quiz < backup_20231201.sql
```