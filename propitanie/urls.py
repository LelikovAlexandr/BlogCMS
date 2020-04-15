from django.contrib import admin
from django.urls import path
from followers.views import new_order, list_of_users, create_order, \
    list_of_orders, get_difference

urlpatterns = [
    path('admin/', admin.site.urls, ),
    path('new_order/', new_order),
    path('users/', list_of_users, name='Users'),
    path('create_order/', create_order, name='New order'),
    path('orders/', list_of_orders, name='Orders'),
    path('difference/', get_difference, name='Difference')
]
