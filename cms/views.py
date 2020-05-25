from operator import attrgetter

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Min, Q, Sum
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_GET
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic import TemplateView
from cms.models import Price
from orders.models import Order
from outer_modules.instagram import get_followers
from users.models import User, UserStatus


# from django.db.models import Count

# User.objects.filter(subscribe_until__gte=timezone.now().date()).values('subscribe_until').annotate(
#     total=Count('subscribe_until'))


@require_GET
@staff_member_required
def dashboard(request):
    added_status = UserStatus.objects.get(name='Added')
    today_users = User.objects.filter(
        Q(date_joined__date=timezone.now().date()) | ~Q(status=added_status))
    number_of_users = number_of_paid_users()
    nearest_unsubscribe_date = User.objects.filter(
        subscribe_until__gt=timezone.datetime.now().date()).aggregate(Min('subscribe_until')).get(
        'subscribe_until__min')
    today_revenue = Order.objects.filter(created_datetime__date=timezone.now().date())
    context = {
        'today_users': sorted(today_users, key=attrgetter('status.id', 'username')),
        'number_of_paid_users': number_of_users,
        'number_of_unsubscribing_users': User.objects.filter(
            subscribe_until=nearest_unsubscribe_date).count(),
        'nearest_unsubscribe_date': nearest_unsubscribe_date,
        'today_revenue': today_revenue.aggregate(Sum('amount')).get('amount__sum') or 0,
        'today_orders_counts': today_revenue.count(),
        'number_of_not_returned_user': not_returned_user().count()
    }
    return render(request, 'cms/dashboard.html', context=context)


def list_to_unsubscribe(request):
    unsubscribe_users = User.objects.filter(subscribe_until=timezone.now().date())
    return render(request, 'cms/unsubscribe.html',
                  context={'unsubscribe_users': unsubscribe_users})


def number_of_paid_users():
    return User.objects.exclude(
        Q(subscribe_until=None) | Q(subscribe_until__lte=timezone.now().date())).count()


def not_returned_user():
    return User.objects.filter(subscribe_until__lte=timezone.now().date())


@require_GET
@staff_member_required
def get_difference(request):
    set_of_followers = get_followers()
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


class PriceCreate(LoginRequiredMixin, CreateView):
    model = Price
    fields = ('price', 'number_of_months')
    template_name = 'cms/create_price.html'
    success_url = reverse_lazy('PriceList')


class PriceList(LoginRequiredMixin, ListView):
    model = Price
    template_name = 'cms/price_list.html'


class PriceUpdate(LoginRequiredMixin, UpdateView):
    model = Price
    fields = ('price', 'number_of_months')
    success_url = reverse_lazy('PriceList')
    template_name = 'cms/update_price.html'


class DeleteVideo(LoginRequiredMixin, DeleteView):
    model = Price
    success_url = reverse_lazy('PriceList')


class PaymentsRules(TemplateView):
    template_name = 'cms/payments_rules.html'


class Confidentiality(TemplateView):
    template_name = 'cms/confidentiality.html'
