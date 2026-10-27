import os
import django
import sys

# Add the project root to the python path
sys.path.append('/home/varshith/Desktop/IP/ignite_admin/Ignite')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ignite_admin.settings')
django.setup()

from website_fixed.models import WebRegistration

print("Records with Test Category:")
regs = WebRegistration.objects.filter(project_category='Test Category')
for reg in regs:
    print(f"ID: {reg.id}, Title: {reg.project_title}, Created: {reg.created_at}")

print("\nRecords with NO Category:")
regs_none = WebRegistration.objects.filter(project_category__isnull=True)
count_none = regs_none.count()
print(f"Count: {count_none}")
if count_none > 0:
    first = regs_none.first()
    print(f"Sample None: ID: {first.id}, Title: {first.project_title}")
