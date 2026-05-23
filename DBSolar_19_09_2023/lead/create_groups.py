#!/usr/bin/env python
"""
Script to create user groups for the CRM system.
Run this after migrations: python create_groups.py
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction


def create_groups():
    """
    Create default user groups and assign permissions
    """
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
            'permissions': []  # Will get all permissions
        }
    }

    created_groups = []

    with transaction.atomic():
        for group_name, group_info in groups_data.items():
            # Create or get group
            group, created = Group.objects.get_or_create(name=group_name)

            if created:
                print(f"✅ Created group: {group_name}")
                created_groups.append(group_name)

                # Add description (using a separate model if you have one, or just print)
                print(f"   Description: {group_info['description']}")

                # Assign permissions if not Admin (Admins get all permissions via is_superuser)
                if group_name != 'Admins' and group_info['permissions']:
                    permissions = Permission.objects.filter(codename__in=group_info['permissions'])
                    group.permissions.set(permissions)
                    print(f"   Assigned {permissions.count()} permissions")
            else:
                print(f"ℹ️ Group already exists: {group_name}")

    return created_groups


def create_sample_users():
    """
    Create sample users for testing
    """
    from django.contrib.auth.models import User

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
        },
        {
            'username': 'admin',
            'password': 'admin123',
            'email': 'admin@example.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'group': 'Admins',
            'is_superuser': True,
            'is_staff': True
        }
    ]

    created_users = []

    for user_data in sample_users:
        group_name = user_data.pop('group')
        password = user_data.pop('password')

        # Check if user exists
        if not User.objects.filter(username=user_data['username']).exists():
            if user_data.get('is_superuser'):
                user = User.objects.create_superuser(**user_data)
            else:
                user = User.objects.create_user(**user_data)

            user.set_password(password)
            user.save()

            # Add to group
            try:
                group = Group.objects.get(name=group_name)
                user.groups.add(group)
                print(f"✅ Created user: {user_data['username']} (Password: {password})")
                created_users.append(user_data['username'])
            except Group.DoesNotExist:
                print(f"⚠️ Group {group_name} not found for user {user_data['username']}")
        else:
            print(f"ℹ️ User already exists: {user_data['username']}")

    return created_users


if __name__ == '__main__':
    print("\n🔧 Setting up CRM user groups...\n")

    # Create groups
    groups = create_groups()

    print("\n👥 Creating sample users...\n")

    # Create sample users
    users = create_sample_users()

    print("\n📊 Summary:")
    print(f"   Groups created: {len(groups)}")
    print(f"   Users created: {len(users)}")

    if users:
        print("\n🔑 Sample Login Credentials:")
        print("   sales1 / password123")
        print("   engineer1 / password123")
        print("   manager1 / password123")
        print("   admin / admin123")

    print("\n✅ Setup complete!")