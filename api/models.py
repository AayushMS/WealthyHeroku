from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class WealthyUserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')
        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class WealthyUser(AbstractBaseUser):
    MALE = "M"
    FEMALE = "F"
    OTHERS = "O"
    SEX_CHOICES = [(MALE, 'Male'), (FEMALE, 'Female'), (OTHERS, 'Others')]
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    date_of_birth = models.DateTimeField(blank=True, null=True)
    sex = models.CharField(max_length=6, blank=True, null=True, choices=SEX_CHOICES)
    country = models.CharField(max_length=50, blank=True, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]
    objects = WealthyUserManager()

    def __str__(self):
        return self.email

    # For checking permissions. to keep it simple all admin have ALL permissons
    def has_perm(self, perm, obj=None):
        return self.is_admin

    # Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)
    def has_module_perms(self, app_label):
        return True


class AccountType(models.Model):
    account_type = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self):
        return self.account_type


class Account(models.Model):
    user = models.ForeignKey(WealthyUser, on_delete=models.CASCADE)
    account_name = models.CharField(max_length=50)
    account_number = models.IntegerField()
    account_type = models.ForeignKey(AccountType, related_name="account", on_delete=models.CASCADE)
    amount = models.IntegerField()

    def __str__(self):
        return str(self.account_number)


class Category(models.Model):
    INCOME = "I"
    EXPENSE = "E"

    CATEGORY_CHOICES = [(INCOME, 'Income'), (EXPENSE, 'Expense')]

    category_name = models.CharField(max_length=255)
    category_type = models.CharField(max_length=1, choices=CATEGORY_CHOICES)


class Transaction(models.Model):
    PAID = "PAID"
    PENDING = "PENDING"

    STATUS_CHOICES = [(PAID, 'Paid'), (PENDING, 'Pending')]

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    amount = models.IntegerField()
    payee = models.CharField(max_length=255)
    created_datetime = models.DateTimeField(auto_now_add=True)
    datetime = models.DateTimeField()
    paid_datetime = models.DateTimeField()
    status = models.CharField(max_length=7, choices=STATUS_CHOICES)
    note = models.CharField(max_length=255)


class Transfer(models.Model):
    PAID = "PAID"
    PENDING = "PENDING"

    STATUS_CHOICES = [(PAID, 'Paid'), (PENDING, 'Pending')]

    from_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="account1")
    to_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="account2")
    title = models.CharField(max_length=50)
    amount = models.IntegerField()
    created_datetime = models.DateTimeField(auto_now_add=True)
    datetime = models.DateTimeField()
    paid_datetime = models.DateTimeField()
    status = models.CharField(max_length=7, choices=STATUS_CHOICES)
    note = models.CharField(max_length=255)


class Goal(models.Model):
    user = models.ForeignKey(WealthyUser, on_delete=models.CASCADE)
    goal_name = models.CharField(max_length=255)
    goal_amount = models.IntegerField()
    current_amount = models.IntegerField()
    created_datetime = models.DateTimeField(auto_now_add=True)
    datetime = models.DateTimeField()
    completion_datetime = models.DateTimeField(blank=True, null=True)
    label = models.CharField(max_length=20)
