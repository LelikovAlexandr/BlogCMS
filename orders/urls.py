from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required

from orders import views

urlpatterns = [
    url(r'^create/$', views.OrderCreate.as_view(), name='OrderCreate'),
    url(r'^list/$', staff_member_required(views.OrderList.as_view()), name='OrdersList'),
    url(r'^(?P<pk>\d+)/delete/$', staff_member_required(views.OrderDelete.as_view()),
        name='DeleteOrder'),
]
