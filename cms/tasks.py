import datetime
import logging
from time import sleep

from celery import shared_task

from cms.models import EmailTemplate
from users.models import User

logger = logging.getLogger(__name__)
DAYS_TO_UNSUBSCRIBE = 3


@shared_task
def send_email(template, recipients, **kwargs):
    if '@' in recipients:
        logger.debug('Sending email to {} with template {}'.format(recipients, template))
        return EmailTemplate.send(template, emails=(recipients,), **kwargs)


@shared_task
def send_unsubscribe_notification():
    for user in User.objects.filter(
            subscribe_until=datetime.datetime.now().date() +
                            datetime.timedelta(DAYS_TO_UNSUBSCRIBE)):
        logger.info('Sending notifications about end of subscription to {}'.format(user.email))
        send_email('DAYS_TO_UNSUBSCRIBE', user.email,
                   context={'DAYS_TO_UNSUBSCRIBE': DAYS_TO_UNSUBSCRIBE})
        sleep(2)
