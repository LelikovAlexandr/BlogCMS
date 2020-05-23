from django.conf.urls import url

from cms import views

urlpatterns = [
    url(r'^$', views.dashboard, name='Dashboard'),
    url(r'^unsubscribe/$', views.list_to_unsubscribe, name='Unsubscribe'),
    url(r'^difference/$', views.get_difference, name='Difference'),
    url(r'^price/$', views.PriceList.as_view(), name='PriceList'),
    url(r'^price/create/$', views.PriceCreate.as_view(), name='PriceCreate'),
    url(r'^price/(?P<pk>\d+)/edit/$', views.PriceUpdate.as_view(), name='PriceUpdate'),
    url(r'^payments_rules/$', views.PaymentsRules.as_view(), name='PaymentsRules'),
]
