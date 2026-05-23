#!/usr/bin/env python
"""
Diagnostic script to check for duplicate apps
"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')

try:
    from django.conf import settings
    from django.apps import apps

    print("=" * 50)
    print("Checking INSTALLED_APPS configuration")
    print("=" * 50)

    # Check INSTALLED_APPS for duplicates
    installed_apps = settings.INSTALLED_APPS
    print(f"\nINSTALLED_APPS ({len(installed_apps)} entries):")

    # Find duplicates
    from collections import Counter

    app_counter = Counter(installed_apps)
    duplicates = [app for app, count in app_counter.items() if count > 1]

    if duplicates:
        print("\n❌ DUPLICATES FOUND:")
        for dup in duplicates:
            print(f"   - {dup} appears {app_counter[dup]} times")
    else:
        print("\n✅ No duplicates found in INSTALLED_APPS")

    # Try to populate apps
    print("\n" + "=" * 50)
    print("Attempting to populate apps...")
    print("=" * 50)

    try:
        apps.populate(settings.INSTALLED_APPS)
        print("✅ Apps populated successfully!")

        # List all registered apps
        print("\nRegistered apps:")
        for app in apps.get_app_configs():
            print(f"   - {app.name} (label: {app.label})")

    except Exception as e:
        print(f"❌ Error: {e}")

except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running this from the correct directory and Django is installed.")