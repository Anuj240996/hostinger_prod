"""
Fix migration dependency issue by updating django_migrations table
Migration 0020 was applied before 0019, but 0020 depends on 0019
We need to insert 0019 into django_migrations with an earlier timestamp
"""
import django
import os
import sys
from datetime import datetime

# Setup Django - add the DBSolar_19_09_2023 directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
django_project_dir = os.path.join(script_dir, 'DBSolar_19_09_2023')
sys.path.insert(0, django_project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventoryproject.settings')

django.setup()

from django.db import connection

print("=" * 60)
print("Fixing Migration Dependency Issue")
print("=" * 60)

cursor = connection.cursor()

try:
    # Check current state
    print("\n1. Checking current migration records...")
    cursor.execute("""
        SELECT app, name, applied 
        FROM django_migrations 
        WHERE app = 'customer' 
        AND name IN ('0019_alter_controller_assignby_alter_controller_assignto_and_more', '0020_alter_customer_cust_id')
        ORDER BY applied;
    """)
    
    migrations = cursor.fetchall()
    print("\nCurrent records:")
    for app, name, applied in migrations:
        print(f"  {name}: Applied at {applied}")
    
    # Check if 0019 exists
    cursor.execute("""
        SELECT COUNT(*) 
        FROM django_migrations 
        WHERE app = 'customer' 
        AND name = '0019_alter_controller_assignby_alter_controller_assignto_and_more';
    """)
    count_0019 = cursor.fetchone()[0]
    
    # Get 0020's applied timestamp
    cursor.execute("""
        SELECT applied 
        FROM django_migrations 
        WHERE app = 'customer' 
        AND name = '0020_alter_customer_cust_id';
    """)
    result_0020 = cursor.fetchone()
    
    if count_0019 == 0 and result_0020:
        print("\n2. Fixing: 0019 is missing, 0020 exists")
        print(f"   0020 was applied at: {result_0020[0]}")
        
        # Insert 0019 with a timestamp 1 minute before 0020
        applied_time = result_0020[0]
        # Make 0019's timestamp earlier than 0020
        if isinstance(applied_time, datetime):
            earlier_time = applied_time.replace(second=applied_time.second - 60)
        else:
            # If it's a string, parse it
            from django.utils.dateparse import parse_datetime
            dt = parse_datetime(str(applied_time))
            if dt:
                earlier_time = dt.replace(second=dt.second - 60)
            else:
                earlier_time = datetime.now()
        
        print(f"   Inserting 0019 with timestamp: {earlier_time}")
        
        cursor.execute("""
            INSERT INTO django_migrations (app, name, applied)
            VALUES ('customer', '0019_alter_controller_assignby_alter_controller_assignto_and_more', %s);
        """, [earlier_time])
        
        connection.commit()
        print("   ✅ Successfully inserted migration 0019!")
        
    elif count_0019 > 0 and result_0020:
        print("\n2. Both migrations exist - checking order...")
        cursor.execute("""
            SELECT applied 
            FROM django_migrations 
            WHERE app = 'customer' 
            AND name = '0019_alter_controller_assignby_alter_controller_assignto_and_more';
        """)
        result_0019 = cursor.fetchone()
        
        if result_0019 and result_0020:
            if result_0019[0] > result_0020[0]:
                print("   ⚠️  0019 was applied AFTER 0020 - this is the problem!")
                print(f"   0019 applied at: {result_0019[0]}")
                print(f"   0020 applied at: {result_0020[0]}")
                print("\n   Fixing: Updating 0019's timestamp to be before 0020...")
                
                # Update 0019's timestamp to be before 0020
                if isinstance(result_0020[0], datetime):
                    earlier_time = result_0020[0].replace(second=result_0020[0].second - 60)
                else:
                    from django.utils.dateparse import parse_datetime
                    dt = parse_datetime(str(result_0020[0]))
                    if dt:
                        earlier_time = dt.replace(second=dt.second - 60)
                    else:
                        earlier_time = datetime.now()
                
                cursor.execute("""
                    UPDATE django_migrations 
                    SET applied = %s
                    WHERE app = 'customer' 
                    AND name = '0019_alter_controller_assignby_alter_controller_assignto_and_more';
                """, [earlier_time])
                
                connection.commit()
                print(f"   ✅ Updated 0019's timestamp to: {earlier_time}")
            else:
                print("   ✅ Order is correct!")
    else:
        print("\n⚠️  Unexpected state. 0020 might not exist.")
    
    # Verify the fix
    print("\n3. Verifying fix...")
    cursor.execute("""
        SELECT app, name, applied 
        FROM django_migrations 
        WHERE app = 'customer' 
        AND name IN ('0019_alter_controller_assignby_alter_controller_assignto_and_more', '0020_alter_customer_cust_id')
        ORDER BY applied;
    """)
    
    migrations = cursor.fetchall()
    print("\nUpdated records (ordered by applied time):")
    for app, name, applied in migrations:
        print(f"  {name}: Applied at {applied}")
    
    print("\n" + "=" * 60)
    print("✅ Fix complete! Now try:")
    print("  python manage.py makemigrations")
    print("  python manage.py migrate")
    print("=" * 60)
    
except Exception as e:
    connection.rollback()
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    cursor.close()
