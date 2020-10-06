from django.core.exceptions import ObjectDoesNotExist

from cms.models import Promocode
from orders.models import Order


def create_order(amount, code=None, is_recurrent=False, is_paid=False):
    try:
        promo_code = Promocode.objects.get(code=code)
    except ObjectDoesNotExist:
        promo_code = None
    order = Order.objects.create(amount=int(float(amount)),
                                 promo_code=promo_code,
                                 is_paid=is_paid,
                                 is_recurrent=is_recurrent,
                                 )
    order.order_id = 'R{}'.format(order.pk) if is_recurrent else 'I{}'.format(order.pk)
    order.save()
    return order.order_id
