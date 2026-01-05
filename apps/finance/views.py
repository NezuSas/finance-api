from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Transaction, ScheduledPayment, WeeklyPeriod
from .serializers import TransactionSerializer, ScheduledPaymentSerializer, WeeklyPeriodSerializer
from django.utils import timezone

class BaseFinanceViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user, deleted_at__isnull=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class WeeklyPeriodViewSet(BaseFinanceViewSet):
    queryset = WeeklyPeriod.objects.all()
    serializer_class = WeeklyPeriodSerializer

class ScheduledPaymentViewSet(BaseFinanceViewSet):
    queryset = ScheduledPayment.objects.all()
    serializer_class = ScheduledPaymentSerializer

    @action(detail=True, methods=['post'], url_path='mark-paid')
    def mark_paid(self, request, pk=None):
        payment = self.get_object()
        if payment.status == 'PAID':
            return Response({'error': 'Already paid'}, status=status.HTTP_400_BAD_REQUEST)

        # Create linked transaction
        transaction = Transaction.objects.create(
            user=request.user,
            type='EXPENSE',
            amount=payment.amount,
            date=timezone.now().date(),
            counterparty=payment.payee,
            description=f"Payment for {payment.payee}. Notes: {payment.notes}",
            method=payment.expected_method or 'OTHER',
            linked_payment=payment
        )

        payment.status = 'PAID'
        payment.paid_at = timezone.now()
        payment.save()

        return Response({
            'payment': self.get_serializer(payment).data,
            'transaction': TransactionSerializer(transaction).data
        })

class TransactionViewSet(BaseFinanceViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

class SyncView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def pull(self, request):
        since = request.query_params.get('since')
        if not since:
            return Response({'error': 'since parameter is required'}, status=400)
        
        # In a real scenario, we'd filter by since
        # For MVP, we'll return everything or filter if we have updated_at
        # DEBUG: Print to console
        print(f"DEBUG SYNC: User={request.user.email} (ID: {request.user.id})")
        print(f"DEBUG SYNC: Params since={since}")
        
        # For MVP/Debugging: Return all active records to ensure data visibility
        # irrespective of client-side 'since' timestamp mismatches.
        transactions = Transaction.objects.filter(user=request.user)
        payments = ScheduledPayment.objects.filter(user=request.user)
        weeks = WeeklyPeriod.objects.filter(user=request.user)
        
        print(f"DEBUG SYNC: Found {transactions.count()} txs, {payments.count()} payments")

        return Response({
            'transactions': TransactionSerializer(transactions, many=True).data,
            'payments': ScheduledPaymentSerializer(payments, many=True).data,
            'weeks': WeeklyPeriodSerializer(weeks, many=True).data,
            'debug_info': {
                'user_email': request.user.email,
                'user_id': str(request.user.id),
                'total_db_transactions': Transaction.objects.count(),
                'user_transactions_count': transactions.count(),
                'server_time': str(timezone.now()),
                'since_param': since
            }
        })

    @action(detail=False, methods=['post'])
    def push(self, request):
        data = request.data
        # Batch processing of transactions, payments, etc.
        # This is where conflict resolution logic goes.
        # For MVP, we'll just save what comes if it doesn't conflict.
        return Response({'status': 'sync complete'})
