import csv
import os
from datetime import datetime
from operator import attrgetter

import requests
from dateutil.relativedelta import relativedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.db.models import Count, Min, Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from cms.models import Article as ArticleModel
from cms.models import Price, Promocode
from orders.models import Order
from users.models import User, UserStatus


def number_of_paid_users():
    """
    Number of paid users
    :return: Number of paid users
    """
    return User.objects.exclude(
        Q(subscribe_until=None) | Q(subscribe_until__lte=timezone.now().date())).count()


def not_returned_user():
    """
    Not returned users
    :return: Queryset of not returned users
    """
    return User.objects.filter(subscribe_until__lte=timezone.now().date())


@staff_member_required
def get_difference(request):
    """
    Show paid by not followers users and followers by not paid users
    """
    # TODO: Добавить отправку списка на отписку в телеграм в формате: https://instagram.com/{
    #  USERNAME}
    if request.method == 'POST':
        file = request.FILES['file']
        decoded_file = file.read().decode('utf-8').splitlines()
        set_of_followers = set()
        for follower in csv.DictReader(decoded_file):
            set_of_followers.add(follower['username'])
        cache.set('followers', set(set_of_followers), 300)
    if cache.get('followers') is None:
        return render(request, 'cms/upload_followers_file.html')
    set_of_followers = cache.get('followers')
    set_of_users = set([user.username for user in User.objects.exclude(
        subscribe_until__lte=timezone.now().date())])
    paid_by_not_followers_set = sorted(
        set(set_of_users) - set(set_of_followers))
    followers_by_not_paid_set = sorted(
        set(set_of_followers) - set(set_of_users))
    paid_by_not_followers = []
    for user in paid_by_not_followers_set:
        paid_by_not_followers.append(User.objects.get(username=user))

    return render(request, 'cms/difference.html', context={
        'paid_by_not_followers': paid_by_not_followers,
        'followers_by_not_paid': followers_by_not_paid_set,
    })


def echo_to_telegram(request):
    """
    Send body of POST request to telegram bot
    """
    from dotenv import load_dotenv
    load_dotenv()

    request_body = dict(request.POST)
    pretty_body = ''
    for key, value in request_body.items():
        pretty_body += '{}: {}\n'.format(key, value)
    bot_id = os.getenv('TELEGRAM_BOT_ID')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    text = 'https://api.telegram.org/{}/sendMessage?chat_id={}&text={}'.format(
        bot_id,
        chat_id,
        pretty_body)
    requests.get(text)
    return HttpResponse('OK', status=200)


def check_promo_code(request):
    promo_code = request.GET.get('promoCode').lower()
    discount = get_object_or_404(Promocode, code=promo_code)
    return JsonResponse(discount.discount, safe=False)


class AdminDashboard(TemplateView):
    """
    Admin's dashboard
    """
    template_name = 'cms/dashboard.html'

    def get_context_data(self, **kwargs):
        added_status = UserStatus.objects.get(name='Added')
        today_users = User.objects.filter(
            Q(date_joined__date=timezone.now().date()) | ~Q(status=added_status))
        number_of_users = number_of_paid_users()
        nearest_unsubscribe_date = User.objects.filter(
            subscribe_until__gt=timezone.datetime.now().date()).aggregate(
            Min('subscribe_until')).get(
            'subscribe_until__min')
        today_revenue = Order.objects.filter(created_datetime__date=timezone.now().date(),
                                             is_paid=True)
        context = super().get_context_data(**kwargs)
        context['today_users'] = sorted(today_users, key=attrgetter('status.id', 'username'))
        context['number_of_paid_users'] = number_of_users
        context['number_of_unsubscribing_users'] = User.objects.filter(
            subscribe_until=nearest_unsubscribe_date).count()
        context['nearest_unsubscribe_date'] = nearest_unsubscribe_date,
        context['today_revenue'] = today_revenue.aggregate(Sum('amount')).get('amount__sum') or 0
        context['today_orders_counts'] = today_revenue.count()
        context['number_of_not_returned_user'] = not_returned_user().count()
        return context


class ListForUnsubscribe(TemplateView):
    """
    Show list for today unsubscribe
    """
    template_name = 'cms/unsubscribe.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        unsubscribe_users = User.objects.filter(subscribe_until=timezone.now().date())
        context['unsubscribe_users'] = unsubscribe_users
        return context


class Article(TemplateView):
    """
    Generate page with article from database
    """
    template_name = 'cms/article.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = get_object_or_404(ArticleModel, slug=self.kwargs['slug'])
        context['caption'] = article.caption
        context['text'] = article.text
        return context


class RecurrentUsers(TemplateView):
    """
    Generate page with list of users with active recurrent payments
    """
    template_name = 'cms/recurrent_users.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.filter(subscribe_until__gte=datetime.now().date(),
                                               recurring_payments=True)
        return context


class PriceCreate(LoginRequiredMixin, CreateView):
    """
    Add new price for period
    """
    model = Price
    fields = ('price', 'number_of_months', 'hidden')
    template_name = 'cms/create_price.html'
    success_url = reverse_lazy('PriceList')


class PriceList(LoginRequiredMixin, ListView):
    """
    Show price list
    """
    model = Price
    template_name = 'cms/price_list.html'


class PriceUpdate(LoginRequiredMixin, UpdateView):
    """
    Update price for period
    """
    model = Price
    fields = ('price', 'number_of_months', 'hidden')
    success_url = reverse_lazy('PriceList')
    template_name = 'cms/update_price.html'


class PriceDelete(LoginRequiredMixin, DeleteView):
    """
    Delete price for period
    """
    model = Price
    success_url = reverse_lazy('PriceList')


class PromoCodeCreate(LoginRequiredMixin, CreateView):
    """
    Add new promo code
    """
    model = Promocode
    fields = '__all__'
    template_name = 'cms/create_promo_code.html'
    success_url = reverse_lazy('PromoCodeList')


class PromoCodeList(LoginRequiredMixin, ListView):
    """
    Show promo code list
    """
    model = Promocode
    template_name = 'cms/promo_code_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all()
        return context


class PromoCodeUpdate(LoginRequiredMixin, UpdateView):
    """
    Update promo code
    """
    model = Promocode
    fields = '__all__'
    success_url = reverse_lazy('PromoCodeList')
    template_name = 'cms/update_promo_code.html'


class PromoCodeDelete(LoginRequiredMixin, DeleteView):
    """
    Delete promo code
    """
    model = Promocode
    success_url = reverse_lazy('PromoCodeList')


class UnsubscribeChart(TemplateView):
    """
    Show chart of unsubscribe users for a month in advance
    """
    template_name = 'cms/unsubscribe_chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chart_data = User.objects.filter(subscribe_until__gte=timezone.now().date(),
                                         subscribe_until__lte=timezone.now().date() + relativedelta(
                                             months=1)).values(
            'subscribe_until').annotate(total=Count('subscribe_until'))
        unsubscribers = []
        days = []
        for day in chart_data:
            unsubscribers.append(int(day.get('total')))
            days.append(float(day.get('subscribe_until').strftime('%d.%m')))
        context['unsubscribers'] = unsubscribers
        context['days'] = days
        return context


class RefundList(TemplateView):
    template_name = 'cms/refunds.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.exclude(refund_choice__isnull=True)
        return context


def handler404(request, exception):
    return render(request, 'errors/404.html', status=404)
