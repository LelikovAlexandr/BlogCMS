from django.conf.urls import url
from django.contrib import admin
from django.urls import path

from followers.views import (UserDelete, UserEdit, get_difference,
                             list_of_orders, list_of_today_users,
                             list_of_users, new_order, change_user_status, LoginUser)

urlpatterns = [
    path('admin/', admin.site.urls, ),
    path('users/', list_of_users, name='Users'),
    path('create_order/', new_order, name='New order'),
    path('orders/', list_of_orders, name='Orders'),
    path('difference/', get_difference, name='Difference'),
    path('', list_of_today_users, name='TodayUsers'),
    path('change_status/', change_user_status, name='ChangeUserStatus'),
    path('accounts/login/', LoginUser.as_view(), name='LogiUser'),
    url(r'^name/(?P<pk>\d+)/edit/$', UserEdit.as_view(), name='UserEdit'),
    url(r'^name/(?P<pk>\d+)/delete/$', UserDelete.as_view(), name='UserDelete')
]
