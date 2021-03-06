from django import template
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.db import models
from django.template import Context

from users.models import User


class Price(models.Model):
    number_of_months = models.IntegerField()
    price = models.IntegerField()
    hidden = models.BooleanField(default=False)

    class Meta:
        ordering = ["number_of_months"]

    def __str__(self):
        return str(self.number_of_months)


class ArticleCategory(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Article(models.Model):
    caption = models.CharField(max_length=150)
    text = models.TextField(default='', null=True, blank=True)
    category = models.ForeignKey(ArticleCategory, on_delete=models.CASCADE,
                                 related_name='category', null=True, blank=True
                                 )
    slug = models.SlugField(max_length=150, default='', null=True, blank=True)

    def __str__(self):
        return self.caption


class Promocode(models.Model):
    code = models.CharField(max_length=50, default=None, null=True)
    discount = models.IntegerField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.owner


class EmailTemplate(models.Model):
    """
    Email templates get stored in database so that admins can
    change emails on the fly
    """
    subject = models.CharField(max_length=255, blank=True, null=True)
    to_email = models.CharField(max_length=255, blank=True, null=True)
    from_email = models.CharField(max_length=255, blank=True, null=True)
    html_template = models.TextField(blank=True, null=True)
    plain_text = models.TextField(blank=True, null=True)
    is_html = models.BooleanField(default=False)
    is_text = models.BooleanField(default=False)

    # unique identifier of the email template
    template_key = models.CharField(max_length=255, unique=True)

    def get_rendered_template(self, tpl, context):
        return self.get_template(tpl).render(context)

    def get_template(self, tpl):
        return template.Template(tpl)

    def get_subject(self, subject, context):
        return subject or self.get_rendered_template(self.subject, context)

    def get_body(self, body, context):
        return body or self.get_rendered_template(self._get_body(), context)

    def get_sender(self):
        return self.from_email or settings.DEFAULT_FROM_EMAIL

    def get_recipient(self, emails, context):
        return emails or [self.get_rendered_template(self.to_email, context)]

    @staticmethod
    def send(*args, **kwargs):
        EmailTemplate._send(*args, **kwargs)

    @staticmethod
    def _send(template_key, context=None, subject=None, body=None, sender=None,
              emails=None, bcc=None, attachments=None):
        if context is None:
            context = dict()
        mail_template = EmailTemplate.objects.get(template_key=template_key)
        context = Context(context)

        subject = mail_template.get_subject(subject, context)
        body = mail_template.get_body(body, context)
        sender = sender or mail_template.get_sender()
        emails = mail_template.get_recipient(emails, context)

        if mail_template.is_text:
            return send_mail(subject, body, sender, emails, fail_silently=not settings.DEBUG)

        msg = EmailMultiAlternatives(subject, body, sender, emails,
                                     alternatives=((body, 'text/html'),),
                                     bcc=bcc
                                     )
        if attachments:
            for name, content, mimetype in attachments:
                msg.attach(name, content, mimetype)
        return msg.send(fail_silently=not settings.DEBUG)

    def _get_body(self):
        if self.is_text:
            return self.plain_text

        return self.html_template

    def __str__(self):
        return "<{}> {}".format(self.template_key, self.subject)
