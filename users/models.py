from django.contrib.auth.models import AbstractUser
from django.db import models
from pytils.translit import slugify

from files.models import File
from videos.models import Video


class UserStatus(models.Model):
    name = models.CharField(max_length=20)
    slug = models.SlugField(max_length=20, default='', null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


REFUND_CHOICE = [
    ('Card', 'Возврат на карту'),
    ('Charity', 'Перевод на благотворительность')
]


class User(AbstractUser):
    subscribe_until = models.DateField(null=True, blank=True)
    status = models.ForeignKey(UserStatus, on_delete=models.CASCADE,
                               related_name='status', default=1)
    available_video = models.ManyToManyField(Video)
    available_file = models.ManyToManyField(File)
    init_password = models.CharField(max_length=10, default='')
    recurring_payments = models.BooleanField(default=False)
    refund_choice = models.CharField(verbose_name='Вариант возврата', choices=REFUND_CHOICE,
                              max_length=10, blank=True, null=True)
    card_number = models.CharField(verbose_name='Номер карты', max_length=100, blank=True, null=True)
    name_for_refund = models.CharField(verbose_name='ФИО', max_length=100, blank=True, null=True)

    class Meta:
        ordering = ["subscribe_until"]

    def __str__(self):
        return self.username


