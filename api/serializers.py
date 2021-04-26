from abc import ABC

from allauth import exceptions
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import Account, Transaction, Category, AccountType, Goal, User
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class AccountTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountType
        fields = '__all__'


class AccountSerializer(serializers.ModelSerializer):
    account_type = AccountTypeSerializer(read_only=False)

    class Meta:
        model = Account
        fields = '__all__'
        extra_kwargs = {'user': {'required': False}}


class ChartDataSerializer(serializers.Serializer):
    category_id = serializers.IntegerField()
    category__category_name = serializers.CharField()
    total = serializers.IntegerField()
    tcount = serializers.IntegerField()


class TransactionSerializer(serializers.ModelSerializer):
    account1 = AccountSerializer(many=False, read_only=True)
    account2 = AccountSerializer(many=False, read_only=True)
    category = CategorySerializer(many=False, read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'


class CreateTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class BalanceChartDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['paid_datetime', 'amount', 'transaction_type']


class CreateAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'
        extra_kwargs = {'user': {'required': False}}


class CreateGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = '__all__'
        extra_kwargs = {'user': {'required': False}}


class GoalSerializer(serializers.ModelSerializer):
    account = AccountSerializer(read_only=False)

    class Meta:
        model = Goal
        fields = '__all__'
        extra_kwargs = {'user': {'required': False}}
