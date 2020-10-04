from django.db.models import Max

from orders.models import Order


def create_order(amount, is_recurrent=False, is_paid=False):
    order = Order.objects.create(amount=int(float(amount)),
                                 is_paid=is_paid,
                                 is_recurrent=is_recurrent)
    order.order_id = 'R{}'.format(order.pk) if is_recurrent else 'I{}'.format(order.pk)
    order.save()
    return order.order_id
