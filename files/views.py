import os

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.encoding import escape_uri_path
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from config.settings import STATIC_URL
from files.models import File, FileCategory
from users.models import User


@login_required
def download(request, slug):
    """
    Generate response with path to file. Protect from unauthorized access
    :param request: Request
    :param slug: File's slug to download
    :return: Response with path to download file
    """
    file = get_object_or_404(File, slug=slug)
    response = HttpResponse(content_type='application/force-download')
    if not request.headers.get('X-Real-Ip'):
        response.status_code = 404
        response.content = 'The request should be come from Nginx server.'
        return response
    is_allowed = True if file in get_object_or_404(User,
                                                   username=request.user).available_file.all() else False
    if not is_allowed:
        response.status_code = 404
        response.content = 'You are not allowed to access this file.'
        return response

    file_name = os.path.basename(file.file.name)
    response['X-Accel-Redirect'] = os.path.join(STATIC_URL, file.file.url[1:])
    response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(
        escape_uri_path(file_name))
    return response


class UploadFile(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    """
    Page with upload file form
    """
    model = File
    fields = '__all__'
    template_name = 'files/upload_file.html'
    success_url = reverse_lazy('FilesList')
    success_message = 'Файл успешно добавлен'

    def form_valid(self, form):
        """
        Add file to active users
        :param form: Form
        :return: Form
        """
        self.object = form.save()
        if self.object.category.available_to_active_subscribers:
            user_list = User.objects.filter(subscribe_until__gt=timezone.now().date())
        else:
            user_list = User.objects.all()
        for user in user_list:
            User.objects.get(username=user.username).available_file.add(self.object)
        return super().form_valid(form)


class FilesList(LoginRequiredMixin, ListView):
    """
    List of uploaded files
    """
    model = File
    template_name = 'files/files_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_list'] = FileCategory.objects.all()
        return context


class UpdateFile(LoginRequiredMixin, UpdateView):
    """
    Edit uploaded file parameters
    """
    model = File
    fields = '__all__'
    template_name = 'files/update_file.html'
    success_url = reverse_lazy('FilesList')


class DeleteFile(LoginRequiredMixin, DeleteView):
    """
    Delete uploaded file
    """
    model = File
    success_url = reverse_lazy('FilesList')


class AddFileCategory(LoginRequiredMixin, CreateView):
    """
    Add new files category
    """
    model = FileCategory
    fields = '__all__'
    template_name = 'files/create_category.html'
    success_url = reverse_lazy('FilesList')


class FileCategoryList(LoginRequiredMixin, ListView):
    """
    List of files category
    """
    model = FileCategory
    template_name = 'files/category_list.html'


class UpdateFileCategory(LoginRequiredMixin, UpdateView):
    """
    Edit files category
    """
    model = FileCategory
    fields = '__all__'
    template_name = 'files/update_category.html'
    success_url = reverse_lazy('FilesList')


class DeleteFileCategory(LoginRequiredMixin, DeleteView):
    """
    Delete files category
    """
    model = FileCategory
    success_url = reverse_lazy('FilesList')
