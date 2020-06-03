from django.db import models
from pytils.translit import slugify


class FileCategory(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, default='', null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class File(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()
    file = models.FileField(upload_to='files/')
    category = models.ForeignKey(FileCategory, on_delete=models.SET_NULL, blank=True, null=True)
    slug = models.SlugField(max_length=150, default='', null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
