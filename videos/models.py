import os

from django.conf import settings
from django.db import models
from django.db.models.functions import Upper
from django.utils import timezone
from pytils.translit import slugify


class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True)
    slug = models.SlugField(max_length=20, default='', null=True, blank=True)

    class Meta:
        ordering = [Upper('name')]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Video(models.Model):
    caption = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    video_code = models.CharField(max_length=20)
    publish_date = models.DateField(default=timezone.now)
    image = models.ImageField(upload_to='images/videos/', default=None, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    slug = models.SlugField(max_length=150, default='', null=True, blank=True)

    class Meta:
        ordering = ["-publish_date"]

    def save(self, *args, **kwargs):
        slug = slugify(self.caption)
        self.slug = '{}-{}'.format(self.id, slug)
        super().save(*args, **kwargs)

    @property
    def get_image_url(self):
        if self.image and hasattr(self.image, 'url'):
            print(self.image.url)
            return os.path.join(settings.STATIC_URL, self.image.url[1:])
        else:
            return os.path.join(settings.STATIC_URL,
                                settings.MEDIA_URL[1:],
                                'images/videos/no_image.png')

    def __str__(self):
        return self.caption
