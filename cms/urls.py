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
    url(r'^promocode/$', staff_member_required(views.PromoCodeList.as_view()), name='PromoCodeList'),
    url(r'^promocode/create/$', staff_member_required(views.PromoCodeCreate.as_view()),
        name='PromoCodeCreate'),
    url(r'^promocode/(?P<pk>\d+)/edit/$', staff_member_required(views.PromoCodeUpdate.as_view()),
        name='PromoCodeUpdate'),
    url(r'^promocode/(?P<pk>\d+)/delete/$', staff_member_required(views.PromoCodeDelete.as_view()),
        name='PromoCodeDelete'),
    url(r'^chart/$', staff_member_required(views.UnsubscribeChart.as_view()),
        name='UnsubscribeChart'),
    url(r'^article/(?P<slug>[\w-]+)/$', views.Article.as_view(), name='Article'),
    url(r'^echo/$', views.echo_to_telegram),
    url(r'^check_code/$', views.check_promo_code),
    url(r'^recurrent_users/$', views.RecurrentUsers.as_view(), name='RecurrentUser'),
    url(r'^refund/$', views.RefundList.as_view(), name='RefundList')
]
