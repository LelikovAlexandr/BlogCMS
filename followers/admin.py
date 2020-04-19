from django.contrib import admin

from followers.models import Order, User

# Register your models here.

admin.site.register(User)
admin.site.register(Order)
