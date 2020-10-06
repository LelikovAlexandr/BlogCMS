from django.db import models

from cms.models import Promocode
from users.models import User


class Order(models.Model):
    order_id = models.CharField(max_length=10, default=0)
    username = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    created_datetime = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    promo_code = models.ForeignKey(Promocode, on_delete=models.SET_NULL, null=True)
    is_paid = models.BooleanField()
    is_recurrent = models.BooleanField(default=False)

    def __str__(self):
        return self.order_id


class RecurrentPayment(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=50)
    amount = models.IntegerField(default=0)
