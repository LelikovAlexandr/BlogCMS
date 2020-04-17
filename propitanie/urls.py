from django.contrib import admin
from django.urls import path
from followers.views import new_order, list_of_users, \
    list_of_orders, get_difference, UserEdit, UserDelete
from django.conf.urls import url

urlpatterns = [
    path('admin/', admin.site.urls, ),
    path('', list_of_users, name='Users'),
    path('create_order/', new_order, name='New order'),
    path('orders/', list_of_orders, name='Orders'),
    path('difference/', get_difference, name='Difference'),
    url(r'^name/(?P<pk>\d+)/edit/$', UserEdit.as_view(), name='UserEdit'),
    url(r'^name/(?P<pk>\d+)/delete/$', UserDelete.as_view(), name='UserDelete')
]
