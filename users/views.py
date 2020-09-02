import json
import logging
import os
from operator import attrgetter
from time import time

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordChangeView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import DeleteView, UpdateView

from cms.models import Price
from files.models import FileCategory
from orders.models import Order
from outer_modules.modulbank import get_signature
from users.forms import UserEditForm
from users.models import User, UserStatus

logger = logging.getLogger(__name__)


@require_POST
def generate_payment(request):
    username = request.POST.get('username').replace('@', '').replace(' ', '').lower()
    email = request.POST.get('email')
    amount = request.POST.get('amount')
    order_id = int(Order.objects.aggregate(Max('order_id')).get('order_id__max')) + 1
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
    Order.objects.create(order_id=order_id, amount=int(float(amount)), is_paid=False)
    return render(request, 'users/generate_payment.html', body)


@require_POST
@staff_member_required
def change_user_status(request):
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
    user = User.objects.get(username=request.user)
    user.recurrrecurring_payments = False
    user.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class UserList(LoginRequiredMixin, TemplateView):
    template_name = 'users/users_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users_list'] = sorted(User.objects.exclude(subscribe_until=None),
                                       key=attrgetter('subscribe_until', 'username'))
        context['authors'] = sorted(User.objects.filter(subscribe_until=None),
                                    key=attrgetter('username'))
        return context


class UserAccount(LoginRequiredMixin, TemplateView):
    template_name = 'users/user_account.html'


class UserFiles(LoginRequiredMixin, ListView):
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
    template_name = 'users/user_login.html'
    pass


class LogoutUser(LoginRequiredMixin, LogoutView):
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


class PasswordResetDone(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'


class PasswordResetConfirm(PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('PasswordResetComplete')


class PasswordResetComplete(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'


class UpdateUser(UpdateView, LoginRequiredMixin):
    model = User
    form_class = UserEditForm
    template_name = 'users/edit_user.html'
    success_url = reverse_lazy('UsersList')


class DeleteUser(DeleteView, LoginRequiredMixin):
    model = User
    success_url = reverse_lazy('UsersList')


class RenewSubscription(TemplateView):
    template_name = 'users/renew_subscription.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prices'] = Price.objects.all()
        return context
