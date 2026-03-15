from django.db import models
from django.contrib.auth.models import User



# Create your models here.
CATEGORY = (
    ('Stationary', 'Stationary'),
    ('Electronics', 'Electronics'),
    ('Food', 'Food'),
)

class Product(models.Model):
    name = models.CharField(max_length=100, null=True)
    quantity = models.PositiveIntegerField(null=True)
    #price = models.PositiveIntegerField(null=True)
    category = models.CharField(max_length=50, choices=CATEGORY, null=True)


    class Meta:
        verbose_name_plural = 'Product'

    def __str__(self):
        return f'{self.name}-{self.quantity}'


class Order(models.Model):
    name = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    order_quantity = models.PositiveIntegerField(null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Order'
    def __str__(self):
        return f'{self.customer}-{self.name}'


class staff_Notification(models.Model):
    staff_id = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=200)
    #created_at = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(null=True,default=0)
    read = models.BooleanField(default=False)
    is_current = models.BooleanField(default=True)  # New field added
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_sent', null=True)

    def __str__(self):
        return f"{self.staff_id.username} - {self.message}"


