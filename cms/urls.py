from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required
from cms import views

urlpatterns = [
    url(r'^$', staff_member_required(views.AdminDashboard.as_view()), name='Dashboard'),
    url(r'^unsubscribe/$', staff_member_required(views.ListForUnsubscribe.as_view()),
        name='Unsubscribe'),
    url(r'^difference/$', views.get_difference, name='Difference'),
    url(r'^price/$', staff_member_required(views.PriceList.as_view()), name='PriceList'),
    url(r'^price/create/$', staff_member_required(views.PriceCreate.as_view()),
        name='PriceCreate'),
    url(r'^price/(?P<pk>\d+)/edit/$', staff_member_required(views.PriceUpdate.as_view()),
        name='PriceUpdate'),
    url(r'^price/(?P<pk>\d+)/delete/$', staff_member_required(views.PriceDelete.as_view()),
        name='PriceDelete'),
    url(r'^chart/$', staff_member_required(views.UnsubscribeChart.as_view()),
        name='UnsubscribeChart'),
    url(r'^article/(?P<slug>[\w-]+)/$', views.Article.as_view(), name='Article'),
    url(r'^echo/$', views.echo_to_telegram),
]
