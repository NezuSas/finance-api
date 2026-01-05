from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet, ScheduledPaymentViewSet, WeeklyPeriodViewSet, SyncView

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'payments', ScheduledPaymentViewSet, basename='payment')
router.register(r'weeks', WeeklyPeriodViewSet, basename='week')
router.register(r'sync', SyncView, basename='sync')

urlpatterns = [
    path('', include(router.urls)),
]
