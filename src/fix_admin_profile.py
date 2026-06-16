#!/usr/bin/env python
"""
Script to fix admin user profile - ensures admin has a UserProfile with role='admin'
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mediresponse.settings')
django.setup()

from django.contrib.auth.models import User
from booking.models import UserProfile

# Get all superusers
superusers = User.objects.filter(is_superuser=True)
print(f"Found {superusers.count()} superuser(s)")

for user in superusers:
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={'role': 'admin'}
    )
    if created:
        print(f"✓ Created UserProfile for {user.username} with role=admin")
    else:
        if profile.role != 'admin':
            profile.role = 'admin'
            profile.save()
            print(f"✓ Updated UserProfile for {user.username} to role=admin")
        else:
            print(f"✓ UserProfile for {user.username} already has role=admin")

print("\nDone! All superusers now have admin profiles.")
