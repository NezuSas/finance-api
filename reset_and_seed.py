import os
import django
from decimal import Decimal
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.accounts.models import User
from apps.finance.models import Transaction, ScheduledPayment, WeeklyPeriod

def smart_seed():
    email = "oscar@nezuecuador.com"
    print(f"--- Smart Seeding for {email} ---")
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        print("User not found! Creating...")
        user = User.objects.create_superuser(username='oscar', email=email, password='Difdesork1996@')

    # Wipe only DATA, keep user
    Transaction.objects.filter(user=user).delete()
    ScheduledPayment.objects.filter(user=user).delete()
    WeeklyPeriod.objects.filter(user=user).delete()
    print("Cleaned existing finance data.")

    # 1. Weekly Period
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    WeeklyPeriod.objects.create(
        user=user,
        week_start_date=monday,
        opening_balance=Decimal("2500.00")
    )

    # 2. Detailed Transactions (Massive Year Generation - 2025)
    import random
    transactions = []
    
    start_date = date(2025, 1, 1)
    end_date = date(2025, 12, 31)
    current = start_date
    
    print(f"Generating data from {start_date} to {end_date}...")

    while current <= end_date:
        # --- Income (15th and 30th) ---
        if current.day == 15 or current.day == 30:
            transactions.append({
                'type': 'INCOME', 'amount': Decimal("3200.00"), 
                'date': current, 'counterparty': "Tech Solutions Inc.", 
                'desc': "Nómina Quincenal", 'method': 'TRANSFER'
            })

        # --- Fixed Expenses (1st and 5th) ---
        if current.day == 1:
            transactions.append({
                'type': 'EXPENSE', 'amount': Decimal("850.00"), 
                'date': current, 'counterparty': "Inmobiliaria Central", 
                'desc': "Renta Mensual", 'method': 'TRANSFER'
            })
        if current.day == 5:
            transactions.append({
                'type': 'EXPENSE', 'amount': Decimal("60.00"), 
                'date': current, 'counterparty': "Claro Internet", 
                'desc': "Servicio Internet", 'method': 'CARD'
            })

        # --- Variable Daily Expenses ---
        
        # 1. Morning Coffee (70% chance)
        if random.random() > 0.3:
            transactions.append({
                'type': 'EXPENSE', 
                'amount': Decimal(random.uniform(3.50, 8.00)).quantize(Decimal("0.01")), 
                'date': current, 
                'counterparty': random.choice(["Starbucks", "Sweet & Coffee", "Juan Valdez", "Cafetería Local"]), 
                'desc': "Café de la mañana", 
                'method': 'CARD'
            })

        # 2. Lunch (Weekdays)
        if current.weekday() < 5: 
            transactions.append({
                'type': 'EXPENSE', 
                'amount': Decimal(random.uniform(6.00, 15.00)).quantize(Decimal("0.01")), 
                'date': current, 
                'counterparty': random.choice(["Subway", "KFC", "Restaurante Ejecutivo", "Uber Eats"]), 
                'desc': "Almuerzo", 
                'method': 'CASH'
            })

        # 3. Groceries (Saturdays or Sundays)
        if current.weekday() == 5: # Saturday
            transactions.append({
                'type': 'EXPENSE', 
                'amount': Decimal(random.uniform(80.00, 150.00)).quantize(Decimal("0.01")), 
                'date': current, 
                'counterparty': "Supermaxi", 
                'desc': "Mercado Semanal", 
                'method': 'CARD'
            })

        # 4. Entertainment/Hobbies (Random ~15% chance)
        if random.random() > 0.85:
            transactions.append({
                'type': 'EXPENSE', 
                'amount': Decimal(random.uniform(20.00, 60.00)).quantize(Decimal("0.01")), 
                'date': current, 
                'counterparty': random.choice(["CineMark", "Steam Games", "Amazon", "Cena Fuera"]), 
                'desc': "Entretenimiento", 
                'method': 'CARD'
            })

        current += timedelta(days=1)

    # Bulk Create for Speed
    print(f"Bulk creating {len(transactions)} transactions...")
    batch_size = 500
    objs = [
        Transaction(
            user=user,
            type=tx['type'],
            amount=tx['amount'],
            date=tx['date'],
            counterparty=tx['counterparty'],
            description=tx['desc'],
            method=tx['method']
        )
        for tx in transactions
    ]
    Transaction.objects.bulk_create(objs, batch_size=batch_size)
    print(f"Successfully created {len(objs)} records.")

    # 3. Scheduled Payments (Future)
    payments = [
        {
            'payee': "Empresa Eléctrica",
            'amount': Decimal("55.20"),
            'due_date': date(2025, 12, 28),
            'status': 'PENDING',
            'notes': "Factura Luz - Vence pronto",
            'method': 'TRANSFER'
        },
        {
            'payee': "Netflix",
            'amount': Decimal("18.00"),
            'due_date': date(2025, 12, 30),
            'status': 'PENDING',
            'notes': "Deducción automática",
            'method': 'CARD'
        }
    ]

    for p in payments:
        payment = ScheduledPayment.objects.create(
            user=user,
            payee=p['payee'],
            amount=p['amount'],
            due_date=p['due_date'],
            status=p['status'],
            notes=p['notes'],
            expected_method=p['method']
        )
        
        # If PAID, link a transaction
        if p['status'] == 'PAID':
            Transaction.objects.create(
                user=user,
                type='EXPENSE',
                amount=p['amount'],
                date=p['due_date'],
                counterparty=p['payee'],
                description=f"Pago Programado: {p['payee']}",
                method=p['method'],
                linked_payment=payment
            )

    print(f"Created {len(payments)} scheduled payments.")
    print("SEEDING COMPLETE. Sync to view changes.")

if __name__ == "__main__":
    smart_seed()
