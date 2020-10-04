import json
import os
from time import time

from orders.services import create_order
from outer_modules.modulbank import get_signature


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
