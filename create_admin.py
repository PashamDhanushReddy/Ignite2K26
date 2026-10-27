import os
import django

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ignite_admin.settings')
django.setup()

from django.contrib.auth.models import User

def ensure_admin():
    username = os.getenv('ADMIN_USERNAME', 'ignite2k27')
    password = os.getenv('ADMIN_PASSWORD', 'Ignite@123')
    email = os.getenv('ADMIN_EMAIL', 'admin@ignite.com')

    user, created = User.objects.get_or_create(username=username, defaults={'email': email})
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.is_active = True
    user.save()

    if created:
        print(f"Superuser '{username}' created successfully.")
    else:
        print(f"Superuser '{username}' updated successfully.")

if __name__ == '__main__':
    ensure_admin()
