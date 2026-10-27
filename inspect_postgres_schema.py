import os
import django
import sys
from django.db import connection

# Add the project root to the python path
sys.path.append('/home/varshith/Desktop/IP/ignite_admin/Ignite')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ignite_admin.settings')
django.setup()

print("Checking column definition in information_schema...")
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT column_name, is_nullable, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'web_registration' AND column_name = 'project_category';
    """)
    result = cursor.fetchone()
    print(f"Column Info: {result}")
