from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from cms import views
from users.views import UserAccount

urlpatterns = [
    url(r'^$', UserAccount.as_view(), name='Main'),
    path('django_admin/', admin.site.urls, ),
    path('video/', include('videos.urls')),
    path('user/', include('users.urls')),
    path('admin/', include('cms.urls')),
    path('order/', include('orders.urls')),
    path('file/', include('files.urls')),
]

handler404 = views.handler404
