import datetime
import logging
import os
from time import sleep

import requests
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist

from cms.models import EmailTemplate
from cms.services import create_payment_body
from orders.models import RecurrentPayment
from users.models import User

logger = logging.getLogger(__name__)
DAYS_TO_UNSUBSCRIBE = 3


@shared_task
def send_post_request(body, url):
    response = requests.post(url, body)
    return response.status_code


@shared_task
def send_email(template, recipients, **kwargs):
    if '@' in recipients:
        logger.debug('Sending email to {} with template {}'.format(recipients, template))
        return EmailTemplate.send(template, emails=(recipients,), **kwargs)


@shared_task
def send_unsubscribe_notification():
    for user in User.objects.filter(
            subscribe_until=datetime.datetime.now().date() +
                            datetime.timedelta(DAYS_TO_UNSUBSCRIBE), recurring_payments=False):
        logger.info('Sending notifications about end of subscription to {}'.format(user.email))
        send_email.delay('DAYS_TO_UNSUBSCRIBE', user.email,
                         context={'DAYS_TO_UNSUBSCRIBE': DAYS_TO_UNSUBSCRIBE})
        sleep(2)


@shared_task
def send_recurrent_payment(days_to_unsubscribe):
    for user in User.objects.filter(subscribe_until=datetime.datetime.now().date() +
                                                    datetime.timedelta(days_to_unsubscribe),
                                    recurring_payments=True):
        try:
            recurrent_payment = RecurrentPayment.objects.get(username_id=user.pk)
        except ObjectDoesNotExist:
            logger.warning('{0} haven\'t transaction id for recurrent payment'.format(user.username))
            continue
        transaction_id = recurrent_payment.transaction_id
        amount = recurrent_payment.amount
        payment_body = create_payment_body(user, transaction_id, amount)
        send_post_request.delay(payment_body, os.getenv('MODULBANK_API_RECURRENT_URL'))
