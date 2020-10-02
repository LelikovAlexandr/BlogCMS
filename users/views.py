import json
import logging
import os
from operator import attrgetter
from time import time

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordChangeView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import DeleteView, UpdateView
from rest_framework.pagination import PageNumberPagination, CursorPagination
from rest_framework.viewsets import ViewSet, ModelViewSet

from cms.models import Price
from files.models import File, FileCategory
from orders.models import Order
from orders.services import incriminate_order_id
from outer_modules.modulbank import get_signature
from users.forms import UserEditForm
from users.models import User, UserStatus
# from users.serializers import UserSerializer
from videos.models import Video

logger = logging.getLogger(__name__)


# TODO: Сделать черный список подписчиков

@require_POST
def generate_payment(request):
    """
    Generate payment params to POST request to Modulbank
    :param request: request
    :return:
    """
    username = request.POST.get('username').replace('@', '').replace(' ', '').lower()
    email = request.POST.get('email')
    amount = request.POST.get('amount')
    is_recurrent = True if request.POST.get('recurrent') else False
    order_id = incriminate_order_id()
    body = {
        'merchant': os.getenv('MODULBANK_MERCHANT_ID'),
        'amount': amount,
        'order_id': order_id,
        'client_name': username,
        'client_email': email,
        'description': 'Оплата доступа в блог',
        'success_url': os.getenv('MODULBANK_SUCCESS_URL'),
        'testing': int(os.getenv('MODULBANK_TEST', 0)),
        'unix_timestamp': int(time()),
        'callback_url': os.getenv('MODULBANK_CALLBACK_URL'),
        'start_recurrent': 1 if is_recurrent else 0,
        'receipt_items': json.dumps({
            'name': 'Оплата доступа в блог',
            'quantity': 1,
            'price': amount,
            'sno': 'usn_income',
            'payment_object': 'commodity',
            'payment_method': 'full_prepayment',
            'vat': 'none'
        })
    }
    signature = {
        'signature': get_signature(
            os.getenv('MODULBANK_TEST_SECRET_KEY')
            if int(body.get('testing')) else
            os.getenv('MODULBANK_SECRET_KEY'), body)
    }
    body.update(signature)
    Order.objects.create(order_id=order_id,
                         amount=int(float(amount)),
                         is_paid=False,
                         is_recurrent=is_recurrent)
    return render(request, 'users/generate_payment.html', body)


@require_POST
@staff_member_required
def change_user_status(request):
    """
    Change user status in system
    :param request: request
    :return:
    """
    data = request.POST.dict()
    user = User.objects.get(username=data.get('username'))
    status = data.get('status')
    logger.info(
        '{} have changed status for user {} from {} to {}'.format(request.user, user.username,
                                                                  user.status, status))
    user.status = UserStatus.objects.get(name=status)
    user.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required()
def recurrent_payments_cancel(request):
    """
    Cancel recurrent payments for user
    :param request: request
    :return:
    """
    user = User.objects.get(username=request.user)
    user.recurring_payments = False
    user.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@staff_member_required
def update_available_video(request, pk):
    """
    Add or delete video from user available video list
    :param request: request
    :param pk: Video ID
    :return:
    """
    action = request.GET.get('action')
    video_id = request.GET.get('id')
    if action == 'add':
        User.objects.get(id=pk).available_video.add(Video.objects.get(id=video_id))
    else:
        User.objects.get(id=pk).available_video.remove(Video.objects.get(id=video_id))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@staff_member_required
def update_available_file(request, pk):
    """
     Add or delete file from user available video list
     :param request: request
     :param pk: File ID
     :return:
     """
    action = request.GET.get('action')
    file_id = request.GET.get('id')
    if action == 'add':
        User.objects.get(id=pk).available_file.add(File.objects.get(id=file_id))
    else:
        User.objects.get(id=pk).available_file.remove(File.objects.get(id=file_id))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class UserList(LoginRequiredMixin, TemplateView):
    """
    List of users
    """
    template_name = 'users/users_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users_list'] = sorted(User.objects.exclude(subscribe_until=None),
                                       key=attrgetter('subscribe_until', 'username'))
        context['authors'] = sorted(User.objects.filter(subscribe_until=None),
                                    key=attrgetter('username'))
        return context


class UserAccount(LoginRequiredMixin, TemplateView):
    """
    User account page
    """
    template_name = 'users/user_account.html'


class UserFiles(LoginRequiredMixin, ListView):
    """
    List of available for user files
    """
    template_name = 'users/files.html'
    context_object_name = 'files'

    def get_queryset(self):
        category = self.kwargs['category']
        return User.objects.get(username=self.request.user).available_file.filter(
            category__slug=category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['caption'] = FileCategory.objects.get(slug=self.kwargs['category']).name
        return context


class LoginUser(LoginView):
    """
    Login page
    """
    template_name = 'users/user_login.html'
    pass


class LogoutUser(LoginRequiredMixin, LogoutView):
    """
    Logout
    """
    next_page = reverse_lazy('LoginUser')


@method_decorator(csrf_exempt, name='dispatch')
class ChangeUserPassword(LoginRequiredMixin, PasswordChangeView):
    template_name = 'users/change_user_password.html'

    def form_valid(self, form):
        self.object = form.save()
        return render(self.request, 'users/change_user_password.html', {'success': True})


class PasswordReset(PasswordResetView):
    template_name = 'users/password_reset.html'
    success_url = reverse_lazy('PasswordResetDone')
    html_email_template_name = 'users/password_reset_email.html'


class PasswordResetDone(TemplateView):
    template_name = 'users/password_reset_done.html'


class PasswordResetConfirm(PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('PasswordResetComplete')


class PasswordResetComplete(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'


class UpdateUser(UpdateView, LoginRequiredMixin):
    """
    Change user parameters
    """
    model = User
    form_class = UserEditForm
    template_name = 'users/edit_user.html'
    success_url = reverse_lazy('UsersList')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['videos'] = Video.objects.all().order_by('caption')
        context['files'] = File.objects.all().order_by('name')
        return context


class DeleteUser(DeleteView, LoginRequiredMixin):
    """
    Delete user
    """
    model = User
    success_url = reverse_lazy('UsersList')


class RenewSubscription(TemplateView):
    """
    Page with payments form
    """
    template_name = 'users/renew_subscription.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prices'] = Price.objects.all()
        return context
