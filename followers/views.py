import datetime
import os

from dateutil.relativedelta import relativedelta
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic.edit import DeleteView, UpdateView
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from dotenv import load_dotenv

from operator import attrgetter

from followers.instagram import get_followers
from followers.models import Order, User, Status
from followers.modulbank import get_signature

load_dotenv()


def new_order(request):
    if request.method == 'POST':
        data = request.POST.dict()
        if get_signature(os.getenv('SECRET_KEY_MODULBANK'), data) == \
                data.get('signature') or data.get('signature') == os.getenv(
            'TEST_SIGNATURE'):
            name = data.get('client_name').replace('@', '').replace(' ',
                                                                    '').lower()
            user, create = User.objects.update_or_create(name=name)
            user.email = data.get('client_email')
            if create:
                start_new_period = timezone.now()
            else:
                start_new_period = max(timezone.now(), user.subscribe_until)
            if data.get('amount') == '350.00':
                user.subscribe_until = start_new_period + relativedelta(
                    months=1)
            elif data.get('amount') == '1800.00':
                user.subscribe_until = start_new_period + relativedelta(
                    months=6)
            user.save()

            order = Order()
            order.username = User.objects.get(name=name)
            order.order_id = data.get('order_id')
            order.amount = data.get('amount')
            order.save()
            message = 'OK'
        else:
            message = 'Signature error'
        return render(request, 'followers/order_status.html',
                      context={'message': message})
    else:
        return render(request, 'followers/create_order.html')


@require_POST
@login_required
def change_user_status(request):
    if request.method == 'POST':
        data = request.POST.dict()
        user = User.objects.get(name=data.get('name'))
        user.status = Status.objects.get(name=data.get('status'))
        user.save()
    return redirect('/')


@require_GET
@login_required
def list_of_users(request):
    all_users = User.objects.filter(subscribe_until__gt=timezone.now())
    return render(request, 'followers/users_list.html',
                  context={'users_list': sorted(all_users,
                                                key=attrgetter(
                                                    'subscribe_until',
                                                    'name'))})


@require_GET
@login_required
def list_of_orders(request):
    all_orders = Order.objects.all()
    return render(request, 'followers/orders_list.html',
                  context={'orders_list': all_orders})


@require_GET
@login_required
def list_of_today_users(request):
    today_users = User.objects.filter(created_date=datetime.date.today())
    today_users_count = today_users.count()
    number_of_users = number_of_paid_users()

    return render(request, 'followers/today_users_list.html',
                  context={'today_users': sorted(today_users,
                                                 key=attrgetter('status.id',
                                                                'name')),
                           'number_of_paid_users': number_of_users,
                           'earning': number_of_users * 350,
                           'today_users_count': today_users_count, }
                  )


def number_of_paid_users():
    return User.objects.filter(
        subscribe_until__lte=datetime.datetime(2021, 1, 1, 14, 51, 13)).count()


@require_GET
@login_required
def get_difference(request):
    set_of_followers = get_followers()
    set_of_users = set([u.name for u in User.objects.exclude(
        subscribe_until__lte=timezone.now())])
    paid_by_not_followers_set = sorted(
        set(set_of_users) - set(set_of_followers))
    followers_by_not_paid_set = sorted(
        set(set_of_followers) - set(set_of_users))
    paid_by_not_followers = []
    for user in paid_by_not_followers_set:
        paid_by_not_followers.append(User.objects.get(name=user))

    return render(request, 'followers/difference.html', context={
        'paid_by_not_followers': paid_by_not_followers,
        'followers_by_not_paid': followers_by_not_paid_set,
    })


class UserStatusEdit(UpdateView, LoginRequiredMixin):
    model = User
    fields = ('status',)
    success_url = reverse_lazy('TodayUsers')


class UserEdit(UpdateView, LoginRequiredMixin):
    model = User
    fields = ('name', 'subscribe_until',)
    template_name = 'followers/name_edit.html'
    success_url = reverse_lazy('Users')


class UserDelete(DeleteView, LoginRequiredMixin):
    model = User
    success_url = reverse_lazy('Users')


class LoginUser(LoginView):
    pass
