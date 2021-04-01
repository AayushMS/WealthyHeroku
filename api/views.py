from django.utils import timezone

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from api.permissions import IsOwner
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from . import serializers
from .models import Account, Transaction, Category, AccountType, Goal, User
from .serializers import AccountSerializer, TransactionSerializer, CategorySerializer, AccountTypeSerializer, \
    GoalSerializer, UserSerializer, CreateAccountSerializer
from rest_framework import viewsets


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class AccountViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsOwner]
    queryset = Account.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.AccountSerializer
        return serializers.CreateAccountSerializer

    def list(self, request, *args, **kwargs):
        query = Account.objects.filter(user=self.request.user)
        serializer = AccountSerializer(instance=query, many=True)

        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # def retrieve(self, request, *args, **kwargs):


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()

    # serializer_class = TransactionSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CreateTransactionSerializer
        return serializers.TransactionSerializer

    def list(self, request, *args, **kwargs):
        print(request.query_params)
        if 'transaction_type' in request.query_params and 'status' in request.query_params:
            print(request.query_params)
            param_transaction_type = request.query_params['transaction_type']
            param_status = request.query_params['status']

            if param_transaction_type == "ALL":
                # timezone.activate()
                queryset = Transaction.objects.filter(account1__user=request.user,
                                                      status=param_status)
                serializer = serializers.TransactionSerializer(instance=queryset, many=True)
                return Response(serializer.data)

            queryset = Transaction.objects.filter(account1__user=request.user,
                                                  transaction_type=param_transaction_type,
                                                  status=param_status)
            serializer = serializers.TransactionSerializer(instance=queryset, many=True)
            return Response(serializer.data)

        if 'chart_data' in request.query_params:
            timezone.deactivate()
            print(request.data['chart_data'])
            start_date = request.query_params['start_date']
            end_date = request.query_params['end_date']
            queryset = Transaction.objects.filter(account1__user=request.user,
                                                  transaction_type=request.data[
                                                      'chart_data'],
                                                  paid_datetime__range=[start_date,
                                                                        end_date],
                                                  status="PAID",
                                                  )
            serializer = TransactionSerializer(instance=queryset, many=True)
            return Response(serializer.data)


        queryset = Transaction.objects.filter(account1__user=request.user)
        serializer = TransactionSerializer(instance=queryset, many=True)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def list(self, request, *args, **kwargs):
        print(request.query_params)
        if 'category_type' in request.query_params:
            print(request.query_params['category_type'])
            queryset = Category.objects.filter(category_type=request.query_params['category_type'])
            serializer = CategorySerializer(instance=queryset, many=True)
            return Response(serializer.data)

        queryset = Category.objects.all()
        serializer = CategorySerializer(instance=queryset, many=True)
        return Response(serializer.data)


class AccountTypeViewSet(viewsets.ModelViewSet):
    serializer_class = AccountTypeSerializer
    queryset = AccountType.objects.all()


class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    queryset = Goal.objects.all()
