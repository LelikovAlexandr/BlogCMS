from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from users.models import User
from videos.models import Tag, Video


class CreateVideo(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    """
    Add new video from Youtube
    """
    model = Video
    fields = '__all__'
    template_name = 'videos/create_video.html'
    success_url = reverse_lazy('VideoList')
    success_message = 'Видео успешно добавлено'

    def form_valid(self, form):
        """
        Add video to active user
        :param form: Form
        :return: Form
        """
        self.object = form.save()
        for user in User.objects.filter(subscribe_until__gte=self.object.publish_date,
                                        date_joined__date__lte=self.object.publish_date):
            User.objects.get(username=user.username).available_video.add(self.object)
        return super().form_valid(form)


class VideosList(LoginRequiredMixin, ListView):
    """
    Video list
    """
    model = Video
    template_name = 'videos/videos_list.html'


class UpdateVideo(LoginRequiredMixin, UpdateView):
    """
    Edit added video parameters
    """
    model = Video
    fields = '__all__'
    template_name = 'videos/update_video.html'
    success_url = reverse_lazy('VideoList')


class DeleteVideo(LoginRequiredMixin, DeleteView):
    """
    Delete video
    """
    model = Video
    success_url = reverse_lazy('VideoList')
