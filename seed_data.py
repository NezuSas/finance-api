import os
import django
import uuid
from decimal import Decimal
from datetime import date, timedelta, datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.accounts.models import User, Profile
from apps.finance.models import Transaction, ScheduledPayment, WeeklyPeriod

def seed_data():
    email = "ocuencamoreno@gmail.com"
    print(f"Seeding data for {email}...")

    # 1. Get or Create User
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'username': 'oscar',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        user.set_password("Difdesork1996@")
        user.save()
        print("User created.")
    else:
        print("User already exists.")

    # 2. Ensure Profile exists
    Profile.objects.get_or_create(
        user=user,
        defaults={
            'display_name': 'Oscar',
            'currency': 'USD',
            'timezone': 'America/Bogota',
            'theme_preference': 'dark'
        }
    )

    # Clean existing data for a fresh example
    Transaction.objects.filter(user=user).delete()
    ScheduledPayment.objects.filter(user=user).delete()
    WeeklyPeriod.objects.filter(user=user).delete()
    print("Cleaned existing finance data.")

    # 3. Weekly Period (Current Monday)
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    WeeklyPeriod.objects.create(
        user=user,
        week_start_date=monday,
        opening_balance=Decimal("2500.00")
    )
    print(f"Created weekly period starting {monday}.")

    # 4. Transactions
    transactions = [
        # Income
        {
            'type': 'INCOME',
            'amount': Decimal("3200.00"),
            'date': monday,
            'counterparty': "Empresa Global Tech",
            'description': "Salario Mensual",
            'method': 'TRANSFER'
        },
        # Expenses
        {
            'type': 'EXPENSE',
            'amount': Decimal("850.00"),
            'date': monday + timedelta(days=1),
            'counterparty': "Inmobiliaria Central",
            'description': "Pago de Renta - Mes Diciembre",
            'method': 'TRANSFER'
        },
        {
            'type': 'EXPENSE',
            'amount': Decimal("45.50"),
            'date': monday + timedelta(days=2),
            'counterparty': "Starbucks",
            'description': "Café y snacks del equipo",
            'method': 'CARD'
        },
        {
            'type': 'EXPENSE',
            'amount': Decimal("120.30"),
            'date': monday + timedelta(days=2),
            'counterparty': "Supermercado Éxito",
            'description': "Compras de la semana",
            'method': 'CARD'
        },
        {
            'type': 'EXPENSE',
            'amount': Decimal("15.99"),
            'date': monday + timedelta(days=3),
            'counterparty': "Netflix",
            'description': "Suscripción Premium",
            'method': 'CARD'
        },
        {
            'type': 'EXPENSE',
            'amount': Decimal("60.00"),
            'date': monday + timedelta(days=4),
            'counterparty': "Uber",
            'description': "Transporte oficina",
            'method': 'APP'
        },
    ]

    for tx_data in transactions:
        # Check if method is valid (fallback to OTHER if not in choices)
        valid_methods = [c[0] for c in Transaction.METHOD_CHOICES]
        method = tx_data['method'] if tx_data['method'] in valid_methods else 'OTHER'
        
        Transaction.objects.create(
            user=user,
            type=tx_data['type'],
            amount=tx_data['amount'],
            date=tx_data['date'],
            counterparty=tx_data['counterparty'],
            description=tx_data['description'],
            method=method
        )
    print(f"Created {len(transactions)} transactions.")

    # 5. Scheduled Payments
    payments = [
        {
            'payee': "Energía Eléctrica",
            'amount': Decimal("85.00"),
            'due_date': today + timedelta(days=5),
            'status': 'PENDING',
            'notes': "Factura bimestral",
            'expected_method': 'TRANSFER'
        },
        {
            'payee': "Internet Fibra Óptica",
            'amount': Decimal("50.00"),
            'due_date': today - timedelta(days=2),
            'status': 'PAID',
            'notes': "Servicio mensual",
            'expected_method': 'TRANSFER'
        },
        {
            'payee': "Seguro Vehicular",
            'amount': Decimal("120.00"),
            'due_date': today + timedelta(days=15),
            'status': 'PENDING',
            'notes': "Cuota 10/12",
            'expected_method': 'CARD'
        }
    ]

    for p_data in payments:
        payment = ScheduledPayment.objects.create(
            user=user,
            payee=p_data['payee'],
            amount=p_data['amount'],
            due_date=p_data['due_date'],
            status=p_data['status'],
            notes=p_data['notes'],
            expected_method=p_data['expected_method']
        )
        
        # If paid, also create a linked transaction
        if p_data['status'] == 'PAID':
            Transaction.objects.create(
                user=user,
                type='EXPENSE',
                amount=p_data['amount'],
                date=p_data['due_date'],
                counterparty=p_data['payee'],
                description=f"Pago programado: {p_data['payee']}",
                method=p_data['expected_method'] if p_data['expected_method'] in [c[0] for c in Transaction.METHOD_CHOICES] else 'OTHER',
                linked_payment=payment
            )
            print(f"Created paid scheduled payment and linked transaction for {p_data['payee']}.")
        else:
            print(f"Created pending scheduled payment for {p_data['payee']}.")

    print("\nSeeding complete! Log in as:")
    print(f"Email: {email}")
    print("Password: Difdesork1996@")

if __name__ == "__main__":
    seed_data()
