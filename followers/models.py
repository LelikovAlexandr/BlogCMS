from django.db import models


class User(models.Model):
    name = models.CharField(max_length=30, unique=True)
    email = models.CharField(max_length=30, null=True)
    subscribe_until = models.DateTimeField(null=True)

    class Meta:
        ordering = ["subscribe_until"]

    def __str__(self):
        return self.name


class Order(models.Model):
    order_id = models.CharField(max_length=10, default=0)
    username = models.ForeignKey(User, on_delete=models.CASCADE,
                                 related_name='username')
    created_datetime = models.DateTimeField(auto_now_add=True)
    amount = models.CharField(max_length=10, default=0)

    def __str__(self):
        return self.order_id
