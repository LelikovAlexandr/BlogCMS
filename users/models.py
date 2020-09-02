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


class User(AbstractUser):
    subscribe_until = models.DateField(null=True, blank=True)
    status = models.ForeignKey(UserStatus, on_delete=models.CASCADE,
                               related_name='status', default=1)
    available_video = models.ManyToManyField(Video)
    available_file = models.ManyToManyField(File)
    init_password = models.CharField(max_length=10, default='')
    recurrrecurring_payments = models.BooleanField(default=False)

    class Meta:
        ordering = ["subscribe_until"]

    def __str__(self):
        return self.username
