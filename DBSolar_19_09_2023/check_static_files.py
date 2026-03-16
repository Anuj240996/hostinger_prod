#!/usr/bin/env python
"""
Diagnostic script to check static files configuration
Run this in your container: python check_static_files.py
"""
import os
from pathlib import Path
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventoryproject.settings')
django.setup()

from django.conf import settings
from django.contrib.staticfiles.finders import get_finders

print("=" * 60)
print("STATIC FILES DIAGNOSTIC")
print("=" * 60)

# Check directories
print("\n1. Checking directories:")
print(f"   BASE_DIR: {settings.BASE_DIR}")
print(f"   STATIC_ROOT: {settings.STATIC_ROOT}")
print(f"   STATIC_URL: {settings.STATIC_URL}")
print(f"   MEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"   MEDIA_URL: {settings.MEDIA_URL}")

print("\n2. STATICFILES_DIRS:")
for dir_path in settings.STATICFILES_DIRS:
    exists = os.path.exists(dir_path)
    print(f"   {dir_path} - {'EXISTS' if exists else 'MISSING'}")
    if exists:
        images_dir = Path(dir_path) / 'images'
        if images_dir.exists():
            logo_files = list(images_dir.glob('dblogo*.png'))
            print(f"      Found {len(logo_files)} logo files in images/")
            for logo in logo_files[:3]:
                print(f"        - {logo.name}")

print("\n3. Checking STATIC_ROOT:")
static_root = Path(settings.STATIC_ROOT)
if static_root.exists():
    print(f"   {static_root} - EXISTS")
    images_dir = static_root / 'images'
    if images_dir.exists():
        logo_files = list(images_dir.glob('dblogo*.png'))
        print(f"      Found {len(logo_files)} logo files in staticfiles/images/")
        for logo in logo_files[:3]:
            print(f"        - {logo.name}")
else:
    print(f"   {static_root} - MISSING (run collectstatic)")

print("\n4. Testing static file finders:")
test_files = ['images/dblogo200.png', 'images/dblogosmall.png']
for test_file in test_files:
    found = False
    for finder in get_finders():
        result = finder.find(test_file)
        if result:
            print(f"   {test_file} - FOUND at {result[0]}")
            found = True
            break
    if not found:
        print(f"   {test_file} - NOT FOUND")

print("\n5. WhiteNoise configuration:")
print(f"   WHITENOISE_USE_FINDERS: {getattr(settings, 'WHITENOISE_USE_FINDERS', 'Not set')}")
print(f"   WHITENOISE_AUTOREFRESH: {getattr(settings, 'WHITENOISE_AUTOREFRESH', 'Not set')}")
print(f"   WHITENOISE_ROOT: {getattr(settings, 'WHITENOISE_ROOT', 'Not set')}")

print("\n6. Middleware check:")
if 'whitenoise.middleware.WhiteNoiseMiddleware' in settings.MIDDLEWARE:
    middleware_index = settings.MIDDLEWARE.index('whitenoise.middleware.WhiteNoiseMiddleware')
    print(f"   WhiteNoiseMiddleware is at position {middleware_index}")
    print(f"   Should be after SecurityMiddleware (position 0)")
else:
    print("   WhiteNoiseMiddleware NOT FOUND in MIDDLEWARE!")

print("\n" + "=" * 60)
print("RECOMMENDATIONS:")
print("=" * 60)
if not static_root.exists() or not list((static_root / 'images').glob('*.png')):
    print("1. Run: python manage.py collectstatic --noinput")
print("2. Check browser console for 404 errors on static files")
print("3. Test URL: http://your-domain/static/images/dblogo200.png")
print("4. Verify files exist in both static/images/ and asert/images/")
