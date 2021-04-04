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
    GoalSerializer, UserSerializer, CreateAccountSerializer, ChartDataSerializer
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
        # print(request.query_params)
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
            # print(request.query_params['chart_data'])
            start_date = request.query_params['start_date']
            end_date = request.query_params['end_date']

            queryset = Transaction.objects.raw('''SELECT * FROM (
                                            SELECT
                                            c.id,
                                            c.category_name,
                                            SUM(t.amount) total
                                            FROM api_transaction t
                                            JOIN api_category c
                                            ON c.id = t.category_id
                                            GROUP BY c.id, c.category_name
                                            ) as foo''')

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

            # income = Transaction.objects.values('paid_datetime') \
            #     .annotate(amount=Sum('amount')) \
            #     .filter(account1__user=request.user,
            #             account1=request.query_params['account_id'],
            #             status='PAID',
            #             transaction_type='INCOME',
            #             paid_datetime__range=[start_date,
            #                                   end_date],
            #             )
            #
            # expense = Transaction.objects.values('paid_datetime') \
            #     .annotate(amount=Sum('amount')) \
            #     .filter(account1__user=request.user,
            #             account1=request.query_params['account_id'],
            #             status='PAID',
            #             transaction_type='EXPENSE',
            #             paid_datetime__range=[start_date,
            #                                   end_date],
            #             )
            #
            # income_transfer = Transaction.objects.values('paid_datetime') \
            #     .annotate(amount=Sum('amount')) \
            #     .filter(account1__user=request.user,
            #             account2=request.query_params['account_id'],
            #             status='PAID',
            #             transaction_type='TRANSFER',
            #             paid_datetime__range=[start_date,
            #                                   end_date],
            #             )
            #
            # expense_transfer = Transaction.objects.values('paid_datetime') \
            #     .annotate(amount=Sum('amount')) \
            #     .filter(account1__user=request.user,
            #             account2=request.query_params['account_id'],
            #             status='PAID',
            #             transaction_type='TRANSFER',
            #             paid_datetime__range=[start_date,
            #                                   end_date],
            #             )

            # nivaja logic start

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

            print(accoount1_trasanctions)
            print(accoount2_trasanctions)
            print("merged: ", all_transactions)

            balance_list = []
            balance_trend = []
            # print(all_transactions)
            balance = 0
            paid_datetime = ''
            tt = {}
            count = 0
            trans = all_transactions
            for t in all_transactions:
                count = count + 1
                if paid_datetime != t['paid_datetime']:
                    print(t)
                    print(trans.reverse()[0])
                    balance_trend.append(tt)
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

            print(balance_trend)
            print("after", all_transactions)

            print(balance_trend)

            print(len(all_transactions), "      ", len(balance_trend))

            print(balance_list)

            # nivaja logic end

            # # List of income dictionaries
            # income_list = []
            #
            # it = []
            # for i in income_transfer:
            #     it.append(i['paid_datetime'])
            #
            # if not income:
            #     for i in income_transfer:
            #         income_list.append(i)
            #
            # for inc in income:
            #     if inc['paid_datetime'] in it:
            #         for i in income_transfer:
            #             if i['paid_datetime'] == inc['paid_datetime']:
            #                 incdict = {'paid_datetime': i['paid_datetime'], 'amount': i['amount'] + inc['amount']}
            #                 income_list.append(incdict)
            #             else:
            #                 income_list.append(i)
            #                 income_list.append(inc)
            #     else:
            #         income_list.append(inc)
            #         for i in income_transfer:
            #             if not i in income_list:
            #                 income_list.append(i)
            #
            # print("income transafer keys: ", it)
            # print("income : ", income)
            # print("income transfer list: ", income_transfer)
            # print("income list: ", income_list)
            #
            # # List of expense dictionaries
            # expense_list = []
            #
            # et = []
            # for e in expense_transfer:
            #     et.append(e['paid_datetime'])
            #
            # if not expense:
            #     for e in expense_transfer:
            #         expense_list.append(e)
            #
            # for exp in expense:
            #     if exp['paid_datetime'] in et:
            #         for e in expense_transfer:
            #             if e['paid_datetime'] == exp['paid_datetime']:
            #                 expdict = {'paid_datetime': e['paid_datetime'], 'amount': e['amount'] + exp['amount']}
            #                 expense_list.append(expdict)
            #             else:
            #                 expense_list.append(e)
            #                 expense_list.append(exp)
            #     else:
            #         expense_list.append(exp)
            #         for e in expense_transfer:
            #             if not e in expense_list:
            #                 expense_list.append(e)
            #
            # # ----------------------------------------------------------------------------------
            # # income - expense dictionary
            # balance_list = []
            #
            # exp_keys = []
            # for exp in expense_list:
            #     exp_keys.append(exp['paid_datetime'])
            #
            # if not income_list:
            #     for exp in expense_list:
            #         expense_list.append(exp)
            #
            # for inc in income_list:
            #     if inc['paid_datetime'] in exp_keys:
            #         for exp in expense_list:
            #             if exp['paid_datetime'] == inc['paid_datetime']:
            #                 expdict = {'paid_datetime': inc['paid_datetime'], 'amount': inc['amount'] - exp['amount']}
            #                 balance_list.append(expdict)
            #             else:
            #                 balance_list.append(inc)
            #                 balance_list.append(exp)
            #     else:
            #         balance_list.append(inc)
            #         for exp in expense_list:
            #             if not exp in balance_list:
            #                 balance_list.append(exp)
            #
            # print("expense keys: ", exp_keys)
            # print("income list: ", income_list)
            # print("expense list: ", expense_list)
            # print("balance list: ", balance_list)

            # serializer = serializers.BalanceChartDataSerializer(instance=balance_list, many=True)
            return JsonResponse(balance_trend, safe=False)

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

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):

        if 'status' in request.query_params:
            queryset = Goal.objects.filter(user=request.user)

        serializer = GoalSerializer(instance=queryset, many=True)
        return Response(serializer.data)
