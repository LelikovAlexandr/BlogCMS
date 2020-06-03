from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from users.models import User
from videos.models import Tag, Video


class CreateVideo(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Video
    fields = '__all__'
    template_name = 'videos/create_video.html'
    success_url = reverse_lazy('VideoList')
    success_message = 'Видео успешно добавлено'

    def form_valid(self, form):
        self.object = form.save()
        for user in User.objects.filter(subscribe_until__gte=self.object.publish_date):
            User.objects.get(username=user.username).available_video.add(self.object)
        return super().form_valid(form)


class VideosList(LoginRequiredMixin, ListView):
    model = Video
    template_name = 'videos/videos_list.html'


class UpdateVideo(LoginRequiredMixin, UpdateView):
    model = Video
    fields = '__all__'
    template_name = 'videos/update_video.html'
    success_url = reverse_lazy('VideoList')


class DeleteVideo(LoginRequiredMixin, DeleteView):
    model = Video
    success_url = reverse_lazy('VideoList')


class AddTag(LoginRequiredMixin, CreateView):
    model = Tag
    fields = '__all__'
    template_name = 'videos/create_tag.html'
    success_url = reverse_lazy('VideoList')


class TagsList(LoginRequiredMixin, ListView):
    model = Tag
    template_name = 'videos/tags_list.html'


class UpdateTag(LoginRequiredMixin, UpdateView):
    model = Tag
    fields = '__all__'
    template_name = 'videos/update_tag.html'
    success_url = reverse_lazy('TagList')


class DeleteTag(LoginRequiredMixin, DeleteView):
    model = Tag
    success_url = reverse_lazy('TagList')
