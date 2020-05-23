from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path

from videos import views

urlpatterns = [
    url(r'^$', staff_member_required(views.VideosList.as_view()), name='VideoList'),
    url(r'^add/$', staff_member_required(views.CreateVideo.as_view()), name='AddVideo'),
    url(r'^(?P<slug>[\w-]+)/edit/$', staff_member_required(views.UpdateVideo.as_view()),
        name='UpdateVideo'),
    url(r'^(?P<slug>[\w-]+)/delete/$', staff_member_required(views.DeleteVideo.as_view()),
        name='DeleteVideo'),
    url(r'^tags/$', views.TagsList.as_view(), name='TagList'),
    url(r'^tag/add$', staff_member_required(views.AddTag.as_view()), name='AddTag'),
    url(r'^tag/(?P<slug>[\w-]+)/edit/$', staff_member_required(views.UpdateTag.as_view()),
        name='UpdateTag'),
    url(r'^tag/(?P<slug>[\w-]+)/delete/$', staff_member_required(views.DeleteTag.as_view()),
        name='DeleteTag'),
]
