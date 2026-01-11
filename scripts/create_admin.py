import os
import django

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
