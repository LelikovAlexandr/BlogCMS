import logging
from operator import attrgetter
from outer_modules.modulbank import is_signature_ok
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import dateformat, timezone
from django.utils.crypto import get_random_string
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, DeleteView
from dotenv import load_dotenv
from django.db import transaction

from cms.models import Price
from cms.tasks import send_email
from files.models import File
from orders.models import Order, RecurrentPayment
from users.models import User, UserStatus

logger = logging.getLogger(__name__)

load_dotenv()


def is_uniq_order(order_id, amount, username):
    """
    Check uniqueness of new order
    :param order_id: Order id
    :param amount: Order amount
    :param username: Username
    :return: True if order isn't in database
    """
    try:
        name = User.objects.get(username=username)
        Order.objects.get(order_id=order_id, amount=amount, username=name)
    except ObjectDoesNotExist:
        return True
    logger.warning('Order {}: Not uniq order'.format(order_id))
    return False


def calculate_new_period(create, user):
    """
    Calculates from which date to add a new period
    :param create: True if user isn't in database
    :param user: User for which the date is calculated
    :return: (Date from which start new period, type of email template)
    """
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


def add_recurrent_payment(username, transaction_id, amount):
    """
    Add new record to RecurrentPayment table in database
    :param username: User who checked recurrent payment checkbox
    :param transaction_id: ID of initial recurrent payment transaction
    :param amount: Order amount for further transaction
    :return: None
    """
    RecurrentPayment.objects.create(username=User.objects.get(username=username),
                                    transaction_id=transaction_id,
                                    amount=amount)


class OrderDelete(DeleteView, LoginRequiredMixin):
    """
    Delete selected order
    """
    model = Order
    success_url = reverse_lazy('OrdersList')


class OrderList(LoginRequiredMixin, TemplateView):
    """
    List of orders
    """
    template_name = 'orders/orders_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders_list'] = sorted(Order.objects.all(), key=attrgetter('created_datetime'),
                                        reverse=True)
        return context


class OrderCreate(CreateView):
    """
    Create new order
    """
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
        transaction_id = data.get('transaction_id')

        if is_signature_ok(data) and is_uniq_order(order_id, amount, username):

            number_of_months = Price.objects.get(price=amount).number_of_months
            user, create = User.objects.update_or_create(username=username)
            if create:
                user.init_password = get_random_string(8)
                user.email = data.get('client_email')
                user.set_password(user.init_password)
            start_new_period, template = calculate_new_period(create, user)
            user.subscribe_until = start_new_period + relativedelta(months=number_of_months)
            user.available_file.add(*File.objects.values_list('id', flat=True))
            user.save()

            formatted_date = dateformat.format(user.subscribe_until, settings.DATE_FORMAT)
            context = {'subscribe_until': formatted_date,
                       'init_password': user.init_password,
                       'username': user.username}

            if settings.DEBUG:
                result = 'Sent email to {}\n with template {}\n and context: {}'.format(
                    user.email, template, context)
            else:
                send_email.delay(template, user.email, context=context)
                result = 'Order created'

            if data.get('is_admin'):
                with transaction.atomic():
                    order_id = int(Order.objects.aggregate(Max('order_id')).get('order_id__max')) + 1
                    Order.objects.create(order_id=order_id, amount=amount, is_paid=False)

            order = Order.objects.get(order_id=order_id)
            order.username = User.objects.get(username=username)
            if not data.get('is_free_user'):
                order.is_paid = True
            if order.is_recurrent:
                user.recurring_payments = True
                add_recurrent_payment(user.username, transaction_id, amount)
                user.save()
            order.save()

            logger.debug(
                'User {} with email {} created successful'.format(user.username, user.email))
        else:
            result = 'Error'

        if data.get('is_admin'):
            return render(request, 'orders/create_order.html', context={'result': result})
        else:
            return HttpResponse('OK', status=200)
