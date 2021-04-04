from django.contrib.auth.hashers import make_password
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, User


# class WealthyUserManager(BaseUserManager):
#     def create_user(self, email, username, password=None):
#         if not email:
#             raise ValueError('Users must have an email address')
#         if not username:
#             raise ValueError('Users must have a username')
#         user = self.model(
#             email=self.normalize_email(email),
#             username=username,
#         )
#
#         user.set_password(make_password(password))
#         user.save(using=self._db)
#         return user
#
#     def create_superuser(self, email, username, password):
#         user = self.create_user(
#             email=self.normalize_email(email),
#             password=password,
#             username=username,
#         )
#         user.is_admin = True
#         user.is_staff = True
#         user.is_superuser = True
#         user.save(using=self._db)
#         return user
#
#
# class WealthyUser(AbstractBaseUser):
#     MALE = "M"
#     FEMALE = "F"
#     OTHERS = "O"
#     SEX_CHOICES = [(MALE, 'Male'), (FEMALE, 'Female'), (OTHERS, 'Others')]
#     email = models.EmailField(verbose_name="email", max_length=60, unique=True)
#     username = models.CharField(max_length=30, unique=True)
#     date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
#     last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
#     is_admin = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)
#     is_superuser = models.BooleanField(default=False)
#     first_name = models.CharField(max_length=25)
#     last_name = models.CharField(max_length=25)
#     date_of_birth = models.DateTimeField(blank=True, null=True)
#     sex = models.CharField(max_length=6, blank=True, null=True, choices=SEX_CHOICES)
#     country = models.CharField(max_length=50, blank=True, null=True)
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username', ]
#     objects = WealthyUserManager()
#
#     def __str__(self):
#         return self.email
#
#     # For checking permissions. to keep it simple all admin have ALL permissons
#     def has_perm(self, perm, obj=None):
#         return self.is_admin
#
#     # Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)
#     def has_module_perms(self, app_label):
#         return True


class AccountType(models.Model):
    account_type = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self):
        return self.account_type


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_name = models.CharField(max_length=50)
    account_number = models.IntegerField()
    account_type = models.ForeignKey(AccountType, related_name="account", on_delete=models.CASCADE)
    amount = models.IntegerField()

    def __str__(self):
        return str(self.account_name)


class Category(models.Model):
    INCOME = "I"
    EXPENSE = "E"

    CATEGORY_CHOICES = [(INCOME, 'Income'), (EXPENSE, 'Expense')]

    category_name = models.CharField(max_length=255)
    category_type = models.CharField(max_length=1, choices=CATEGORY_CHOICES)


class Transaction(models.Model):
    PAID = "PAID"
    PENDING = "PENDING"

    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
    TRANSFER = "TRANSFER"

    STATUS_CHOICES = [(PAID, 'Paid'), (PENDING, 'Pending')]
    TYPE_CHOICES = [(INCOME, 'Income'), (EXPENSE, 'Expense'), (TRANSFER, 'Transfer')]

    account1 = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="account1")
    account2 = models.ForeignKey(Account, on_delete=models.CASCADE, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    transaction_type = models.CharField(max_length=8, choices=TYPE_CHOICES)
    title = models.CharField(max_length=50)
    amount = models.IntegerField()
    payee = models.CharField(max_length=255, blank=True, null=True)
    created_datetime = models.DateField(auto_now_add=True)
    datetime = models.DateField()
    paid_datetime = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=7, choices=STATUS_CHOICES)
    note = models.CharField(max_length=255, blank=True)
    picture = models.ImageField(null=True, blank=True)

    def __str__(self):
        return str(self.title)


class Goal(models.Model):
    REACHED = "REACHED"
    PENDING = "PENDING"

    STATUS_CHOICES = [(REACHED, 'Reached'), (PENDING, 'Pending')]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal_name = models.CharField(max_length=255)
    target_amount = models.IntegerField()
    current_amount = models.IntegerField()
    created_date = models.DateField(auto_now_add=True)
    completed_date = models.DateField(blank=True, null=True)
    desired_date = models.DateField()
    note = models.CharField(max_length=255, blank=True, null=True)
    priority = models.IntegerField()
    status = models.CharField(max_length=7, choices=STATUS_CHOICES)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
