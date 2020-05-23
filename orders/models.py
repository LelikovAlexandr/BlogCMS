from django.db import models

from users.models import User


# Create your models here.
class Order(models.Model):
    order_id = models.CharField(max_length=10, default=0)
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    created_datetime = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()

    def __str__(self):
        return self.order_id
