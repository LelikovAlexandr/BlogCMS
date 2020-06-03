from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required

from files import views

urlpatterns = [
    url(r'^$', staff_member_required(views.FilesList.as_view()), name='FilesList'),
    url(r'^download/(?P<slug>[\w-]+)/$', views.download, name='Download'),
    url(r'^add/$', staff_member_required(views.UploadFile.as_view()), name='UploadFile'),
    url(r'^(?P<slug>[\w-]+)/edit/$', staff_member_required(views.UpdateFile.as_view()),
        name='UpdateFile'),
    url(r'^(?P<slug>[\w-]+)/delete/$', staff_member_required(views.DeleteFile.as_view()),
        name='DeleteFile'),
    url(r'^categories/$', views.FileCategoryList.as_view(), name='CategoryList'),
    url(r'^category/add$', staff_member_required(views.AddFileCategory.as_view()), name='AddCategory'),
    url(r'^category/(?P<slug>[\w-]+)/edit/$', staff_member_required(views.UpdateFileCategory.as_view()),
        name='UpdateCategory'),
    url(r'^category/(?P<slug>[\w-]+)/delete/$', staff_member_required(views.DeleteFileCategory.as_view()),
        name='DeleteCategory'),
]
