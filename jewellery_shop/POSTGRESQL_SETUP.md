# ZYRA Jewels - PostgreSQL setup

The project now uses PostgreSQL only (`jewellery_project/settings.py`). SQLite is no longer configured.
`db.sqlite3` is kept only as a source for moving your existing data.

## 1. Install and create the database

```bash
pip install -r requirements.txt
createdb zyra          # or: CREATE DATABASE zyra; in psql
```

## 2. Set connection variables (defaults shown)

| Variable     | Default     |
|--------------|-------------|
| PGDATABASE   | zyra        |
| PGUSER       | postgres    |
| PGPASSWORD   | (empty)     |
| PGHOST       | localhost   |
| PGPORT       | 5432        |
| PGSSLMODE    | prefer      |

PowerShell: `$env:PGPASSWORD="your-password"`  |  bash: `export PGPASSWORD=your-password`

## 3. Create tables

```bash
python manage.py migrate
python manage.py createsuperuser   # only if starting fresh
```

## 4. (Optional) Move existing SQLite data

Only needed if you want the customers/products/orders in `db.sqlite3`. Using your OLD project copy (still on SQLite), export:

```bash
python manage.py dumpdata --natural-foreign --natural-primary --exclude=contenttypes --exclude=auth.permission --exclude=sessions --exclude=admin.logentry --exclude=shop.metalprice --output=database-transfer.json
```

Copy `database-transfer.json` into this project, then (after step 3):

```bash
python manage.py loaddata database-transfer.json
```

Never commit `database-transfer.json` (it contains customer data and password hashes). Product images stay in `media/`.

## 5. Run

```bash
python manage.py runserver
```
