import os
import django
import sys
from django.db import connection

# Add the project root to the python path
sys.path.append('/home/varshith/Desktop/IP/ignite_admin/Ignite')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ignite_admin.settings')
django.setup()

with connection.cursor() as cursor:
    cursor.execute("PRAGMA table_info(web_registration)")
    columns = [row[1] for row in cursor.fetchall()]
    print("Columns in web_registration:", columns)
