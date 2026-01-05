import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.accounts.models import User
from apps.finance.models import Transaction

def inspect():
    print("--- Database Inspection ---")
    users = User.objects.all()
    print(f"Total Users: {users.count()}")
    for u in users:
        tx_count = Transaction.objects.filter(user=u).count()
        print(f"User: {u.email} (ID: {u.id})")
        print(f"  Transactions: {tx_count}")
        if tx_count > 0:
            print("  Sample:", Transaction.objects.filter(user=u).first())

if __name__ == "__main__":
    inspect()
