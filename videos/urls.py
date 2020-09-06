from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required

from videos import views

urlpatterns = [
    url(r'^$', staff_member_required(views.VideosList.as_view()), name='VideoList'),
    url(r'^add/$', staff_member_required(views.CreateVideo.as_view()), name='AddVideo'),
    url(r'^(?P<slug>[\w-]+)/edit/$', staff_member_required(views.UpdateVideo.as_view()),
        name='UpdateVideo'),
    url(r'^(?P<slug>[\w-]+)/delete/$', staff_member_required(views.DeleteVideo.as_view()),
        name='DeleteVideo'),
]
