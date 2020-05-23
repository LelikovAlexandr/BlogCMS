import os
from operator import attrgetter

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import dateformat, timezone
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, DeleteView
from dotenv import load_dotenv

from cms.models import Price
from cms.tasks import send_email
from orders.models import Order
from outer_modules.modulbank import get_signature
from users.models import User, UserStatus
import logging

logger = logging.getLogger(__name__)

load_dotenv()


def is_signature_ok(data):
    signature = data.get('signature')
    if (get_signature(os.getenv('MODULBANK_SECRET_KEY'), data) == signature
            or get_signature(os.getenv('MODULBANK_TEST_SECRET_KEY'), data) == signature
            or os.getenv('MODULBANK_TEST_SIGNATURE') == signature):
        return True
    else:
        logger.warning('Order {}: Signature error'.format(data.get('order_id')))
        return False


def is_uniq_order(order_id, amount, username):
    try:
        name = User.objects.get(username=username)
        Order.objects.get(order_id=order_id, amount=amount, username=name)
    except ObjectDoesNotExist:
        return True
    logger.warning('Order {}: Not uniq order'.format(order_id))
    return False


def calculate_new_period(create, user):
    if create:
        start_new_period = timezone.now().date()
        template = 'NEW_USER'
        logger.debug('Start creating user {}'.format(user.username))
    else:
        start_new_period = max(timezone.now().date(), user.subscribe_until)
        template = 'SUBSCRIPTION_RENEWAL'
        if not user.subscribe_until > timezone.now().date():
            user.status = UserStatus.objects.get(name='Renewal')
            template = 'RETURNED_USER'
    return start_new_period, template


class OrderDelete(DeleteView, LoginRequiredMixin):
    model = Order
    success_url = reverse_lazy('OrdersList')


class OrderList(LoginRequiredMixin, TemplateView):
    template_name = 'orders/orders_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders_list'] = sorted(Order.objects.all(), key=attrgetter('created_datetime'),
                                        reverse=True)
        return context


class OrderCreate(CreateView):
    model = Order
    fields = '__all__'
    template_name = 'orders/create_order.html'
    success_url = reverse_lazy('Main')
    extra_context = {'all_price': Price.objects.order_by('number_of_months')}

    def post(self, request, *args, **kwargs):
        data = request.POST.dict()
        username = data.get('client_name').replace('@', '').replace(' ', '').lower()
        amount = int(float(data.get('amount')))
        order_id = data.get('order_id')

        if is_signature_ok(data) and is_uniq_order(order_id, amount, username):

            number_of_months = Price.objects.get(price=amount).number_of_months
            user, create = User.objects.update_or_create(username=username)
            user.email = data.get('client_email')
            start_new_period, template = calculate_new_period(create, user)
            user.subscribe_until = start_new_period + relativedelta(months=number_of_months)
            user.save()

            formatted_date = dateformat.format(user.subscribe_until, settings.DATE_FORMAT)
            context = {'subscribe_until': formatted_date}
            if settings.DEBUG:
                result = 'Sent email to {}\n with template {}\n and context: {}'.format(
                    user.email, template, context)
            else:
                send_email.delay(template, user.email, context=context)
                result = 'Order created'
            order = Order()
            order.username = User.objects.get(username=username)
            order.order_id = order_id
            order.amount = amount
            order.save()
            logger.debug('User {} with email {} created successful'.format(user.username, user.email))
        else:
            result = 'Error'
        return render(request, 'orders/create_order.html', context={'result': result})
