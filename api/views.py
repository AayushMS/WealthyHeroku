from django.db.models import Avg, Sum, Count, IntegerField
from django.utils import timezone

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from api.permissions import IsOwner
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models.expressions import RawSQL, When, Case, Value

from . import serializers
from .models import Account, Transaction, Category, AccountType, Goal, User
from .serializers import AccountSerializer, TransactionSerializer, CategorySerializer, AccountTypeSerializer, \
    CreateGoalSerializer, UserSerializer, CreateAccountSerializer, ChartDataSerializer
from rest_framework import viewsets


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class AccountViewSet(viewsets.ModelViewSet):
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


class ReportsViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()

    def list(self, request, *args, **kwargs):
        if 'start_date' in request.query_params and 'end_date' in request.query_params and 'outlook' not in request.query_params:
            start_date = request.query_params['start_date']
            end_date = request.query_params['end_date']

            transactions_query = Transaction.objects.values('paid_datetime',
                                                            'amount', 'transaction_type') \
                .filter(account1__user=request.user,
                        status='PAID',
                        paid_datetime__range=[start_date,
                                              end_date],
                        ).order_by('paid_datetime')
            balance_list = []
            balance_trend = []
            balance = 0
            paid_datetime = ''
            tt = {}

            for t in transactions_query:

                if paid_datetime != t['paid_datetime'] and tt != {}:
                    balance_trend.append(tt)
                if t == transactions_query[len(transactions_query) - 1]:
                    balance_trend.append(t)
                paid_datetime = t['paid_datetime']
                if t['transaction_type'] == 'INCOME':
                    balance += t['amount']
                elif t['transaction_type'] == 'EXPENSE':
                    balance -= t['amount']
                t['balance'] = balance
                balance_list.append(balance)
                tt = t

            return JsonResponse(balance_trend, safe=False)

        if 'start_date' in request.query_params and 'end_date' in request.query_params and 'outlook' in request.query_params:
            start_date = request.query_params['start_date']
            end_date = request.query_params['end_date']

            income_dict = Transaction.objects \
                .filter(account1__user=request.user,
                        status='PAID',
                        paid_datetime__range=[start_date,
                                              end_date],
                        transaction_type='INCOME'
                        ).aggregate(total_income=Sum('amount'))

            expense_dict = Transaction.objects \
                .filter(account1__user=request.user,
                        status='PAID',
                        paid_datetime__range=[start_date,
                                              end_date],
                        transaction_type='EXPENSE'
                        ).aggregate(total_expense=Sum('amount'))

            planned_income_dict = Transaction.objects \
                .filter(account1__user=request.user,
                        status='PENDING',
                        transaction_type='INCOME'
                        ).aggregate(total_planned_income=Sum('amount'))

            planned_expense_dict = Transaction.objects \
                .filter(account1__user=request.user,
                        status='PENDING',
                        transaction_type='EXPENSE'
                        ).aggregate(total_planned_expense=Sum('amount'))

            latest_plan = Transaction.objects.latest('datetime').datetime

            print(latest_plan)

            # try:
            #     balance = income_dict['total_income'] - expense_dict['total_expense']
            # except:
            #     balance = 0
            print(income_dict['total_income'])
            print(expense_dict['total_expense'])
            balance = income_dict['total_income'] - expense_dict['total_expense']
            outlook = {'total_income': income_dict['total_income'], 'total_expense': expense_dict['total_expense'],
                       'balance': balance,
                       'total_planned_income': planned_income_dict['total_planned_income'],
                       'total_planned_expense': planned_expense_dict['total_planned_expense'], 'last_date': latest_plan}

            return JsonResponse(outlook, safe=False)


class ChartsViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()

    def list(self, request, *args, **kwargs):
        if 'chart_data' in request.query_params:
            timezone.deactivate()
            start_date = request.query_params['start_date']
            end_date = request.query_params['end_date']

            # category chart data
            queryset = Transaction.objects.values('category_id', 'category__category_name').annotate(
                total=Sum('amount')).annotate(tcount=Count('id')) \
                .filter(account1__user=request.user,
                        transaction_type=request.query_params[
                            'chart_data'],
                        paid_datetime__range=[start_date,
                                              end_date],
                        status="PAID"
                        )

            serializer = ChartDataSerializer(instance=queryset, many=True)
            return Response(serializer.data)

        if 'account_id' in request.query_params:
            start_date = request.query_params['start_date']
            end_date = request.query_params['end_date']

            accoount1_trasanctions = Transaction.objects.values('paid_datetime', 'amount', 'transaction_type',
                                                                'account1', 'account2') \
                .filter(account1__user=request.user,
                        account1=request.query_params['account_id'],
                        status='PAID',
                        paid_datetime__range=[start_date,
                                              end_date],
                        )

            accoount2_trasanctions = Transaction.objects.values('paid_datetime', 'amount', 'transaction_type',
                                                                'account1', 'account2') \
                .filter(account1__user=request.user,
                        account2=request.query_params['account_id'],
                        status='PAID',
                        paid_datetime__range=[start_date,
                                              end_date],
                        )
            all_transactions = accoount1_trasanctions.union(accoount2_trasanctions)

            balance_list = []
            balance_trend = []
            balance = 0
            paid_datetime = ''
            tt = {}

            for t in all_transactions:

                if paid_datetime != t['paid_datetime'] and tt != {}:
                    balance_trend.append(tt)
                if t == all_transactions[len(all_transactions) - 1]:
                    balance_trend.append(t)
                paid_datetime = t['paid_datetime']
                if t['transaction_type'] == 'INCOME':
                    balance += t['amount']
                elif t['transaction_type'] == 'EXPENSE':
                    balance -= t['amount']
                elif t['transaction_type'] == 'TRANSFER' and t['account1'] == int(request.query_params['account_id']):
                    balance -= t['amount']
                elif t['transaction_type'] == 'TRANSFER' and t['account2'] == int(request.query_params['account_id']):
                    balance += t['amount']
                t['balance'] = balance
                balance_list.append(balance)
                tt = t

            return JsonResponse(balance_trend, safe=False)


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CreateTransactionSerializer
        if self.action == 'partial_update':
            return serializers.CreateTransactionSerializer
        return serializers.TransactionSerializer

    def list(self, request, *args, **kwargs):
        # print(request.query_params)

        if 'transaction_type' in request.query_params and 'status' in request.query_params and 'recent_transactions' in request.query_params:
            param_transaction_type = request.query_params['transaction_type']
            param_status = request.query_params['status']

            if param_transaction_type == "ALL":
                # timezone.activate()
                queryset = Transaction.objects.filter(account1__user=request.user,
                                                      status=param_status).order_by('datetime')[:5]
                serializer = serializers.TransactionSerializer(instance=queryset, many=True)
                return Response(serializer.data)

        if 'transaction_type' in request.query_params and 'status' in request.query_params:
            print(request.query_params)
            param_transaction_type = request.query_params['transaction_type']
            param_status = request.query_params['status']

            if param_transaction_type == "ALL":
                # timezone.activate()
                queryset = Transaction.objects.filter(account1__user=request.user,
                                                      status=param_status).order_by('datetime')
                serializer = serializers.TransactionSerializer(instance=queryset, many=True)
                return Response(serializer.data)

            queryset = Transaction.objects.filter(account1__user=request.user,
                                                  transaction_type=param_transaction_type,
                                                  status=param_status).order_by('datetime')
            serializer = serializers.TransactionSerializer(instance=queryset, many=True)
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
    serializer_class = CreateGoalSerializer
    queryset = Goal.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.GoalSerializer
        return serializers.CreateGoalSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        if 'status' in request.query_params:
            queryset = Goal.objects.filter(user=request.user,
                                           status=request.query_params['status']
                                           )
            print(queryset)

        serializer = CreateGoalSerializer(instance=queryset, many=True)
        return Response(serializer.data)

    # def partial_update(self, request, *args, **kwargs):
    #     if 'paid_date' in request.query_params and 'status' in request.query_params:
    #
