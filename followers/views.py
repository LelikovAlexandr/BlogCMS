from django.shortcuts import render
from followers.models import User, Order
from followers.modulbank import get_signature
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from dotenv import load_dotenv
import os
from followers.instagram import get_followers
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy
import datetime

load_dotenv()


def new_order(request):
    if request.method == 'POST':
        data = request.POST.dict()
        if get_signature(os.getenv('TEST_SECRET_KEY_MODULBANK'), data) == \
                data.get('signature') or data.get('signature') == os.getenv(
            'TEST_SIGNATURE'):
            user, create = User.objects.update_or_create(
                name=data.get('client_name')
            )
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
            order.username = User.objects.get(name=data.get('client_name'))
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


def list_of_users(request):
    all_users = User.objects.filter(subscribe_until__gt=timezone.now())
    return render(request, 'followers/users_list.html',
                  context={'users_list': all_users})


def list_of_orders(request):
    all_orders = Order.objects.all()
    return render(request, 'followers/orders_list.html',
                  context={'orders_list': all_orders})


#
def list_of_today_users(request):
    today_users = User.objects.filter(created_date=datetime.date.today())
    return render(request, 'followers/today_users_list.html',
                  context={'today_users': today_users})

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


class UserEdit(UpdateView):
    model = User
    fields = ('name', 'subscribe_until',)
    template_name = 'followers/name_edit.html'
    success_url = reverse_lazy('Users')


class UserDelete(DeleteView):
    model = User
    success_url = reverse_lazy('Users')
