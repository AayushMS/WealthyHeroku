from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import WealthyUser, Account, Transaction, Category, AccountType, Goal, Transfer
from .serializers import WealthyUserSerializer, AccountSerializer, TransactionSerializer, CategorySerializer, \
    AccountTypeSerializer, GoalSerializer, TransferSerializer
from rest_framework import viewsets


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = WealthyUserSerializer
    queryset = WealthyUser.objects.all()


class AccountViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def list(self, request, *args, **kwargs):
        query = Account.objects.filter(user=self.request.user)
        serializer = AccountSerializer(instance=query, many=True)

        return Response(serializer.data)


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class AccountTypeViewSet(viewsets.ModelViewSet):
    serializer_class = AccountTypeSerializer
    queryset = AccountType.objects.all()


class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    queryset = Transaction.objects.all()


class TransferViewSet(viewsets.ModelViewSet):
    serializer_class = TransferSerializer
    queryset = Transaction.objects.all()
