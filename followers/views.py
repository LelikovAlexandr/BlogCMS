from django.shortcuts import render, redirect
from followers.models import User, Order
from followers.modulbank import get_signature
from dateutil.relativedelta import relativedelta
import requests
from django.utils import timezone
from dotenv import load_dotenv
import os

load_dotenv()


def new_order(request):
    message = 'Method error'
    if request.method == 'POST':
        data = request.POST.dict()
        # if get_signature(os.getenv('TEST_SECRET_KEY_MODULBANK'), data) == \
        #         data['signature']:
        user, create = User.objects.update_or_create(
            name=data['client_name'],
        )
        user.email = data['client_email']
        if data['amount'] == '350':
            user.subscribe_until = timezone.now() + relativedelta(
                months=1)
        elif data['amount'] == '1800':
            user.subscribe_until = timezone.now() + relativedelta(
                months=6)
        user.save()

        order = Order()
        order.username = User.objects.get(name=data['client_name'])
        order.order_id = data['order_id']
        order.amount = data['amount']
        order.save()
        message = 'OK'
        # else:
        #     message = 'Signature error'

    return render(request, 'followers/index.html',
                  context={'message': message})


def list_of_users(request):
    all_users = User.objects.all()
    return render(request, 'followers/users_list.html',
                  context={'users_list': all_users})


def list_of_orders(request):
    all_orders = Order.objects.all()
    return render(request, 'followers/orders_list.html',
                  context={'orders_list': all_orders})


def create_order(request):
    if request.method == 'POST':
        requests.post('http://127.0.0.1:8000/new_order/',
                      data=request.POST.dict())
        return redirect('/users')
    else:
        return render(request, 'followers/create_order.html')


def get_difference(request):
    set_of_followers = {'Polina', 'Julia'}
    set_of_users = set([u.name for u in User.objects.all()])
    paid_by_not_followers = sorted(set(set_of_users) - set(set_of_followers))
    followers_by_not_paid = sorted(set(set_of_followers) - set(set_of_users))
    return render(request, 'followers/difference.html', context={
        'paid_by_not_followers': paid_by_not_followers,
        'followers_by_not_paid': followers_by_not_paid,
    })
