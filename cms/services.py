import json
import os
from time import time

import requests
from django.core.cache import cache
from django.utils import timezone
from dotenv import load_dotenv
from requests import request

from orders.services import create_order
from outer_modules.modulbank import get_signature

load_dotenv()


def create_payment_body(user, transaction_id, amount):
    body = {
        'merchant': os.getenv('MODULBANK_MERCHANT_ID'),
        'first_recurrent_transaction': transaction_id,
        'amount': amount,
        'order_id': create_order(amount),
        'description': 'Оплата доступа в блог',
        'testing': int(os.getenv('MODULBANK_TEST', 0)),
        'callback_url': os.getenv('MODULBANK_CALLBACK_URL'),
        'client_name': user.username,
        'client_email': user.email,
        'unix_timestamp': int(time()),
        'receipt_items': json.dumps({
            'name': 'Оплата доступа в блог',
            'quantity': 1,
            'price': amount,
            'sno': 'usn_income',
            'payment_object': 'commodity',
            'payment_method': 'full_prepayment',
            'vat': 'none'
        })
    }
    signature = {
        'signature': get_signature(
            os.getenv('MODULBANK_TEST_SECRET_KEY')
            if int(body.get('testing')) else
            os.getenv('MODULBANK_SECRET_KEY'), body)
    }
    body.update(signature)
    return body


def send_to_telegram(count):
    body = f'И еще {count} новых человек'
    bot_id = os.getenv('TELEGRAM_BOT_ID')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    text = 'https://api.telegram.org/{}/sendMessage?chat_id={}&text={}'.format(
        bot_id,
        chat_id,
        body)
    requests.get(text)


def send_every_ten_customer():
    headers = {
        "user-agent": "WooCommerce API Client-Python",
        "accept": "application/json",
        "Authorization": f"Basic {os.getenv('WOOCOMMERCE_TOKEN')}"
    }
    orders = request(method='GET', url='https://lelikova.ru/wp-json/wc/v3/orders',
                     headers=headers).json()
    last_order_time = cache.get('last_order_time', timezone.now().strftime('%Y-%m-%dT%H:%M:%S'))
    orders_count = cache.get('orders_count', 0)

    filtered_orders = list(filter(lambda order:
                                  int(order.get('total')) > 8500 and
                                  order.get('status') == 'processing' and
                                  order.get('date_modified') > last_order_time, orders))
    new_orders_count = len(filtered_orders)

    if new_orders_count:
        last_order_time = sorted(filtered_orders, key=lambda order: order.get('date_modified'))[
            -1].get('date_modified')
        orders_count += new_orders_count
        if orders_count >= 10:
            send_to_telegram(orders_count)
            cache.set('orders_count', 0)
        else:
            cache.set('orders_count', orders_count, timeout=60 * 60 * 24 * 7)
    cache.set('last_order_time', last_order_time)
