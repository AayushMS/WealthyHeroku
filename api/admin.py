from django.contrib import admin
from .models import WealthyUser, Account, Transaction, Category, AccountType, Goal, Transfer

# Register your models here.
admin.site.register(WealthyUser)
admin.site.register(Account)
admin.site.register(Transaction)
admin.site.register(Category)
admin.site.register(AccountType)
admin.site.register(Goal)
admin.site.register(Transfer)

