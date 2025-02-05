from django.contrib.auth.hashers import make_password, check_password
from django.db import models

# 管理员和用户
class manager(models.Model):
    manager_id = models.AutoField(primary_key=True)
    manager_name = models.CharField(max_length=20, unique=True, null=False)
    manager_password = models.CharField(max_length=20, null=False)

    class Meta:
        db_table = "manager"
        verbose_name = "manager"

class user_accounts(models.Model):
    GENDER_CHOICES = [
        (0, '男'),
        (1, '女'),
    ]

    user_id = models.AutoField(primary_key=True)
    user_email = models.EmailField(unique=True, null=False)
    user_name = models.CharField(max_length=40, null=False)
    user_password = models.CharField(max_length=128, null=False)
    user_balance = models.FloatField(default=2e5, null=False)
    user_age = models.IntegerField(null=True)
    user_sex = models.IntegerField(choices=GENDER_CHOICES, null=True)
    phone_number = models.CharField(max_length=15, null=True)
    address = models.CharField(max_length=100, null=True)
    remark = models.TextField(max_length=500, null=True)
    status = models.BooleanField(default=True, null=False)

    class Meta:
        db_table = "user_accounts"
        verbose_name = "user accounts"

    def setPassword(self, row_password):
        self.user_password = make_password(password=row_password)

    def checkPassword(self, row_password):
        return check_password(row_password, self.user_password)

# 隔天更新，数据源来自Tushare的股票列表
class stock_basic(models.Model):
    stock_code = models.CharField(max_length=9, primary_key=True)
    stock_name = models.CharField(max_length=20, null=False)
    industry = models.CharField(max_length=20, null=True)
    area = models.CharField(max_length=20, null=True)
    list_date = models.CharField(max_length=8, null=False)
    update_date = models.DateTimeField(auto_now_add=True, null=False)

    class Meta:
        db_table = "stock_basic"
        verbose_name = "stock basic"

# 年度股票日线行情数据
class stock_market(models.Model):
    market_id = models.AutoField(primary_key=True)
    stock_code = models.CharField(max_length=9, null=False)
    trade_date = models.CharField(max_length=8, null=False)
    open = models.FloatField(null=False)
    high = models.FloatField(null=False)
    low = models.FloatField(null=False)
    close = models.FloatField(null=False)
    pct_chg = models.FloatField(null=False)
    vol = models.IntegerField(null=False)
    amount = models.FloatField(null=False)

    class Meta:
        db_table = "stock_market"
        verbose_name = "stock market"
        unique_together = ("stock_code", "trade_date")
        indexes = [models.Index(fields=["stock_code", "trade_date"])]

# 持有股记录
class stock_ownership(models.Model):
    ownership_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(user_accounts, on_delete=models.CASCADE, db_column="user_id")
    stock_code = models.CharField(max_length=9, null=False)
    stock_name = models.CharField(max_length=20, null=False)
    hold_number = models.IntegerField(null=False)
    purchase_per_price = models.FloatField(null=False)

    class Meta:
        db_table = "stock_ownership"
        verbose_name = "stock ownership"

# 股票交易记录
class stock_transactions(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        (0, '买入'),
        (1, '卖出'),
    ]

    transaction_id = models.AutoField(primary_key=True)
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE_CHOICES, null=False)
    transaction_date = models.DateTimeField(auto_now_add=True, null=False)
    user_id = models.ForeignKey(user_accounts, on_delete=models.CASCADE, db_column="user_id")
    stock_code = models.CharField(max_length=9, null=False)
    stock_name = models.CharField(max_length=20, null=False)
    transaction_number = models.IntegerField(null=False)
    per_price = models.FloatField(null=False)
    gains = models.FloatField(default=0, null=False)

    class Meta:
        db_table = "stock_transactions"
        verbose_name = "stock transactions"