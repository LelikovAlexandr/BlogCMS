from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required

from users import views

urlpatterns = [
    url(r'^account/$', views.UserAccount.as_view(), name='UserAccount'),
    url(r'^files/(?P<category>[\w-]+)$', views.UserFiles.as_view(), name='UserFiles'),
    url(r'^login/$', views.LoginUser.as_view(), name='LoginUser'),
    url(r'^logout/$', views.LogoutUser.as_view(), name='LogoutUser'),
    url(r'change_password/', views.ChangeUserPassword.as_view(), name='ChangeUserPassword'),
    url(r'password_reset/', views.PasswordReset.as_view(), name='PasswordReset'),
    url(r'password_reset_done/', views.PasswordResetDone.as_view(), name='PasswordResetDone'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.PasswordResetConfirm.as_view(),
        name='password_reset_confirm'),
    url(r'password_reset_complete/', views.PasswordResetComplete.as_view(),
        name='PasswordResetComplete'),
    url(r'^(?P<pk>\d+)/delete/$', staff_member_required(views.DeleteUser.as_view()),
        name='UserDelete'),
    url(r'^(?P<pk>\d+)/edit/$', staff_member_required(views.UpdateUser.as_view()),
        name='UserEdit'),
    url(r'^(?P<pk>\d+)/edit/available_video/$',
        staff_member_required(views.update_available_video),
        name='UpdateAvailableVideo'),
    url(r'^(?P<pk>\d+)/edit/available_file/$',
        staff_member_required(views.update_available_file),
        name='UpdateAvailableFile'),
    url(r'^change_status/$', staff_member_required(views.change_user_status),
        name='ChangeUserStatus'),
    url(r'^list/$', staff_member_required(views.UserList.as_view()), name='UsersList'),
    url('^renew/$', views.RenewSubscription.as_view(), name='RenewSubscription'),
    url('^renew/generate_payment/$', views.generate_payment, name='GeneratePayment'),
    url('^recurrent_payments_cancel/$', views.recurrent_payments_cancel,
        name='RecurrentPaymentsCancel')
]
