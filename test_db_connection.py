"""
Script to test PostgreSQL database connection
Run this to verify your database credentials work
"""
import psycopg2
from psycopg2 import sql

# Test connection with different configurations
configs = [
    {
        'name': 'Current settings (root user)',
        'host': 'localhost',
        'database': 'db_solar',
        'user': 'root',
        'password': 'Anuj@25032503',
        'port': 5432
    },
    {
        'name': 'Default postgres user',
        'host': 'localhost',
        'database': 'db_solar',
        'user': 'postgres',
        'password': 'Anuj@25032503',
        'port': 5432
    },
    {
        'name': 'postgres user, postgres database',
        'host': 'localhost',
        'database': 'postgres',
        'user': 'postgres',
        'password': 'Anuj@25032503',
        'port': 5432
    }
]

print("Testing PostgreSQL connections...")
print("=" * 60)

for config in configs:
    print(f"\nTrying: {config['name']}")
    print(f"  Host: {config['host']}")
    print(f"  Database: {config['database']}")
    print(f"  User: {config['user']}")
    print(f"  Port: {config['port']}")
    
    try:
        conn = psycopg2.connect(
            host=config['host'],
            database=config['database'],
            user=config['user'],
            password=config['password'],
            port=config['port']
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"  ✓ SUCCESS! Connected to PostgreSQL")
        print(f"  Version: {version[0][:50]}...")
        
        # Check if db_solar exists
        cursor.execute("SELECT datname FROM pg_database WHERE datname = 'db_solar';")
        db_exists = cursor.fetchone()
        if db_exists:
            print(f"  ✓ Database 'db_solar' exists")
        else:
            print(f"  ✗ Database 'db_solar' does NOT exist")
        
        # List all users
        cursor.execute("SELECT usename FROM pg_user;")
        users = cursor.fetchall()
        print(f"  Available users: {', '.join([u[0] for u in users])}")
        
        cursor.close()
        conn.close()
        print(f"\n✅ This configuration works! Use this in settings.py")
        break
        
    except psycopg2.OperationalError as e:
        print(f"  ✗ FAILED: {str(e)[:80]}")
    except Exception as e:
        print(f"  ✗ ERROR: {str(e)[:80]}")

print("\n" + "=" * 60)
print("\nIf all connections failed:")
print("1. Make sure PostgreSQL is running")
print("2. Check if database 'db_solar' exists")
print("3. Verify username and password are correct")
print("4. Check PostgreSQL authentication settings (pg_hba.conf)")
