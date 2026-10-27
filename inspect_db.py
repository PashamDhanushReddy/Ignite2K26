import os
import django
import sys

# Add the project root to the python path
sys.path.append('/home/varshith/Desktop/IP/ignite_admin/Ignite')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ignite_admin.settings')
django.setup()

from website_fixed.models import WebRegistration

print("Distinct Project Categories:")
print(list(WebRegistration.objects.values_list('project_category', flat=True).distinct()))

print("\nDistinct Idea Themes:")
print(list(WebRegistration.objects.values_list('idea_theme', flat=True).distinct()))
