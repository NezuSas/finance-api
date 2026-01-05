from rest_framework import serializers
from .models import Transaction, ScheduledPayment, WeeklyPeriod

class WeeklyPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyPeriod
        fields = '__all__'
        read_only_fields = ['user']

class ScheduledPaymentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ScheduledPayment
        fields = '__all__'
        read_only_fields = ['user']

class TransactionSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    method_display = serializers.CharField(source='get_method_display', read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['user']
