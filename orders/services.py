from django.db.models import Max

from orders.models import Order


def incriminate_order_id():
    try:
        order_id = int(Order.objects.aggregate(Max('order_id')).get('order_id__max')) + 1
    except TypeError:
        order_id = 1
    return order_id
