from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from cms.models import Article, EmailTemplate, Price
from orders.models import Order
from users.models import User
from videos.models import Video

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Order)
admin.site.register(Price)
admin.site.register(EmailTemplate)
admin.site.register(Video)
admin.site.register(Article)
