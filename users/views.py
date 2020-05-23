from operator import attrgetter

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetView, \
    PasswordResetConfirmView, PasswordResetDoneView, PasswordResetCompleteView
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from django.views.generic.edit import DeleteView, UpdateView
from django.views.decorators.csrf import csrf_exempt
from users.forms import UserEditForm
from users.models import User, UserStatus
from django.utils.decorators import method_decorator
from django.shortcuts import render
import logging

logger = logging.getLogger(__name__)


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
