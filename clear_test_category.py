import os
import django
import sys

# Add the project root to the python path
sys.path.append('/home/varshith/Desktop/IP/ignite_admin/Ignite')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ignite_admin.settings')
django.setup()

from website_fixed.models import WebRegistration

print("Updating records with 'Test Category' to empty string...")
# Use empty string '' instead of None because column is NOT NULL
updated_count = WebRegistration.objects.filter(project_category='Test Category').update(project_category='')
print(f"Successfully updated {updated_count} records.")

print("\nVerifying...")
remaining = WebRegistration.objects.filter(project_category='Test Category').count()
print(f"Remaining records with 'Test Category': {remaining}")

print("\nDistinct Project Categories now:")
# Filter out empty strings to see what remains
categories = list(WebRegistration.objects.exclude(project_category='').values_list('project_category', flat=True).distinct())
print(categories)
