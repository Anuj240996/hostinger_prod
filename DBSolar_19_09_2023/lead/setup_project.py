
#!/usr/bin/env python
"""
Complete project setup script
Run this after cloning the project
"""

import os
import sys
import subprocess
import django


def run_command(command):
    """Run a shell command and print output"""
    print(f"\n> {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")
    return result.returncode == 0


def main():
    print("=" * 50)
    print("Solar CRM - Complete Setup")
    print("=" * 50)

    # Step 1: Make migrations
    print("\n📦 Creating migrations...")
    apps = ['core', 'leads', 'pipeline', 'surveys', 'quotations', 'revenue', 'analytics', 'team', 'settings']

    for app in apps:
        run_command(f"python manage.py makemigrations {app}")

    # Step 2: Apply migrations
    print("\n🗄️  Applying migrations...")
    if not run_command("python manage.py migrate"):
        print("❌ Migration failed!")
        return

    # Step 3: Setup Django environment for script
    print("\n🔧 Setting up Django environment...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
    django.setup()

    # Step 4: Create groups
    print("\n👥 Creating user groups...")
    from django.contrib.auth.models import Group, Permission

    groups_data = {
        'Sales': {
            'description': 'Sales representatives who manage leads and quotations',
            'permissions': [
                'add_lead', 'change_lead', 'view_lead',
                'add_leadactivity', 'change_leadactivity', 'view_leadactivity',
                'add_followup', 'change_followup', 'view_followup',
                'add_quotation', 'change_quotation', 'view_quotation',
                'add_revenue', 'view_revenue',
            ]
        },
        'Engineers': {
            'description': 'Engineers who perform site surveys',
            'permissions': [
                'view_lead',
                'add_survey', 'change_survey', 'view_survey',
                'add_surveyimage', 'change_surveyimage', 'view_surveyimage',
                'view_quotation',
            ]
        },
        'Managers': {
            'description': 'Managers who oversee sales team',
            'permissions': [
                'add_lead', 'change_lead', 'view_lead', 'delete_lead',
                'view_leadactivity',
                'view_followup',
                'add_quotation', 'change_quotation', 'view_quotation', 'delete_quotation',
                'add_survey', 'change_survey', 'view_survey',
                'add_revenue', 'change_revenue', 'view_revenue',
                'view_analytics',
                'view_team',
            ]
        },
        'Admins': {
            'description': 'System administrators with full access',
            'permissions': []
        }
    }

    for group_name, group_info in groups_data.items():
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            print(f"   ✅ Created group: {group_name}")
            if group_name != 'Admins' and group_info['permissions']:
                permissions = Permission.objects.filter(codename__in=group_info['permissions'])
                group.permissions.set(permissions)
                print(f"      Added {permissions.count()} permissions")
        else:
            print(f"   ℹ️ Group already exists: {group_name}")

    # Step 5: Create superuser if not exists
    print("\n👤 Creating superuser...")
    from django.contrib.auth.models import User

    if not User.objects.filter(is_superuser=True).exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        print("   ✅ Created superuser: admin / admin123")
    else:
        print("   ℹ️ Superuser already exists")

    # Step 6: Create sample users
    print("\n🧪 Creating sample users...")

    sample_users = [
        {
            'username': 'sales1',
            'password': 'password123',
            'email': 'sales1@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'group': 'Sales'
        },
        {
            'username': 'engineer1',
            'password': 'password123',
            'email': 'engineer1@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'group': 'Engineers'
        },
        {
            'username': 'manager1',
            'password': 'password123',
            'email': 'manager1@example.com',
            'first_name': 'Robert',
            'last_name': 'Johnson',
            'group': 'Managers'
        }
    ]

    for user_data in sample_users:
        group_name = user_data.pop('group')
        password = user_data.pop('password')

        if not User.objects.filter(username=user_data['username']).exists():
            user = User.objects.create_user(**user_data)
            user.set_password(password)
            user.save()

            # Add to group
            try:
                group = Group.objects.get(name=group_name)
                user.groups.add(group)
                print(f"   ✅ Created user: {user_data['username']} / {password}")
            except Group.DoesNotExist:
                print(f"   ⚠️ Group {group_name} not found for user {user_data['username']}")
        else:
            print(f"   ℹ️ User already exists: {user_data['username']}")

    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("=" * 50)
    print("\n📊 Login Credentials:")
    print("   Admin:     admin / admin123")
    print("   Sales:     sales1 / password123")
    print("   Engineer:  engineer1 / password123")
    print("   Manager:   manager1 / password123")
    print("\n🚀 Run the server: python manage.py runserver")
    print("   Access the app: http://127.0.0.1:8000")


if __name__ == '__main__':
    main()