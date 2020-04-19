from django.db import models


class Status(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class User(models.Model):
    name = models.CharField(max_length=30, unique=True)
    email = models.CharField(max_length=30, null=True)
    created_date = models.DateField(auto_now_add=True)
    subscribe_until = models.DateTimeField(null=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE,
                               related_name='status', default=1)

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
