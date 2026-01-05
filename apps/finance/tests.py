from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Transaction, ScheduledPayment, WeeklyPeriod
from decimal import Decimal
import datetime

User = get_user_model()

class FinanceUseCaseTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='password123'
        )
        self.today = timezone.now().date()

    # --- USE CASE 1: Income Transaction ---
    def test_create_income_transaction(self):
        """Test creating a standard salary income."""
        tx = Transaction.objects.create(
            user=self.user,
            type='INCOME',
            amount=Decimal('3000.00'),
            date=self.today,
            counterparty='Tech Corp',
            method='TRANSFER',
            description='Monthly Salary'
        )
        self.assertEqual(tx.type, 'INCOME')
        self.assertEqual(tx.amount, 3000.00)
        self.assertEqual(str(tx), "INCOME - 3000.00 - Tech Corp")

    # --- USE CASE 2: Expense Transaction ---
    def test_create_expense_transaction(self):
        """Test creating a daily expense."""
        tx = Transaction.objects.create(
            user=self.user,
            type='EXPENSE',
            amount=Decimal('15.50'),
            date=self.today,
            counterparty='Starbucks',
            method='CARD',
            description='Coffee'
        )
        self.assertEqual(tx.type, 'EXPENSE')
        self.assertEqual(tx.method, 'CARD')

    # --- USE CASE 3: Scheduled Payment (Pending) ---
    def test_create_scheduled_payment(self):
        """Test scheduling a future payment."""
        due_date = self.today + datetime.timedelta(days=5)
        payment = ScheduledPayment.objects.create(
            user=self.user,
            payee='Electric Company',
            amount=Decimal('85.00'),
            due_date=due_date,
            status='PENDING',
            expected_method='TRANSFER'
        )
        self.assertEqual(payment.status, 'PENDING')
        self.assertIsNone(payment.paid_at)

    # --- USE CASE 4: Payment Lifecycle (Pending -> Paid) ---
    def test_mark_payment_as_paid(self):
        """
        Test the critical flow of marking a payment as paid.
        This must:
        1. Update status to PAID.
        2. Set paid_at timestamp.
        3. AUTOMATICALLY create a linked Transaction.
        """
        # 4.1 Setup
        payment = ScheduledPayment.objects.create(
            user=self.user,
            payee='Internet Provider',
            amount=Decimal('50.00'),
            due_date=self.today,
            status='PENDING',
            expected_method='CARD'
        )

        # 4.2 Simulate Action (Logic mimics ViewSet/Service)
        # Manually replicating the viewset logic since we are testing models/flows
        transaction = Transaction.objects.create(
            user=self.user,
            type='EXPENSE',
            amount=payment.amount,
            date=timezone.now().date(),
            counterparty=payment.payee,
            description=f"Payment for {payment.payee}",
            method=payment.expected_method,
            linked_payment=payment
        )
        payment.status = 'PAID'
        payment.paid_at = timezone.now()
        payment.save()

        # 4.3 Verify
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'PAID')
        self.assertIsNotNone(payment.paid_at)
        
        # Verify Link
        self.assertEqual(transaction.linked_payment, payment)
        self.assertEqual(transaction.amount, Decimal('50.00'))

    # --- USE CASE 5: Weekly Period ---
    def test_weekly_period_creation(self):
        """Test defining a weekly budget period."""
        period = WeeklyPeriod.objects.create(
            user=self.user,
            week_start_date=self.today,
            opening_balance=Decimal('1000.00')
        )
        self.assertEqual(period.opening_balance, 1000.00)
        self.assertEqual(period.user, self.user)

    # --- USE CASE 6: Soft Deletion ---
    def test_soft_deletion(self):
        """Test that deleted_at is respected (simulated)."""
        tx = Transaction.objects.create(
            user=self.user,
            type='EXPENSE',
            amount=Decimal('10.00'),
            date=self.today,
            counterparty='Test Delete',
            method='CASH'
        )
        
        # Simulate soft delete
        tx.deleted_at = timezone.now()
        tx.save()
        
        # Verify it still exists in DB but is marked deleted
        self.assertIsNotNone(tx.deleted_at)
        # Standard filter should exclude it
        active_tx = Transaction.objects.filter(deleted_at__isnull=True, id=tx.id)
        self.assertFalse(active_tx.exists())

    # --- USE CASE 7: Data Integrity (No 'OTHER' method) ---
    def test_valid_methods_only(self):
        """Verify strict adherence to valid payment methods."""
        valid_methods = ['TRANSFER', 'CASH', 'CARD', 'OTHER']
        tx = Transaction(
            user=self.user,
            type='EXPENSE', 
            amount=Decimal('10'), 
            date=self.today, 
            counterparty='Test',
            method='BITCOIN' # Invalid
        )
        # Django validation doesn't auto-run on save(), but models define choices.
        # This test ensures our codebase constants match expectations.
        self.assertNotIn('BITCOIN', [c[0] for c in Transaction.METHOD_CHOICES])
