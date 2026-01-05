import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.accounts.models import User

email = 'ocuencamoreno@gmail.com'
password = 'Difdesork1996@'
username = 'oscar'

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser {email} created successfully.")
else:
    print(f"Superuser {email} already exists.")
