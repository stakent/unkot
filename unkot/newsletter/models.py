import secrets

from django.core.mail import send_mail
from django.db import models
from django.urls import reverse
from django.utils import timezone

from unkot.users.models import User


class Subscriber(models.Model):
    """
    Subscriber stores information about subscriber preferences
    in newsletter context.
    """

    email = models.EmailField(primary_key=True)
    user = models.ForeignKey(
        User, blank=True, default=None, null=True, on_delete=models.SET_NULL
    )
    active = models.BooleanField(default=False)
    activation_token = models.CharField(max_length=200, default="")
    activation_action_ts = models.DateTimeField(blank=True, null=True)
    activation_email_sent_ts = models.DateTimeField(blank=True, null=True)
    deactivation_ts = models.DateTimeField(blank=True, null=True)
    last_email_sent_ts = models.DateTimeField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse('newsletter_subscriber', kwargs={'pk': self.pk})

    def send_activation_email(self):
        if self.active:
            return
        if self.activation_token == '':
            self.activation_token = secrets.token_urlsafe()
        activation_url = (
            f'https://unkot.pl/newsletter/activate/{ self.activation_token }/'
        )
        subject = 'aktywacja subskrybcji newsletter unkot.pl'
        msg = 'W celu potwierdzenia subskrybcji newsletter unkot.pl '
        msg += 'prosimy o odwiedzenie poniżego linku aktywacyjnego.\n'
        msg += f'{ activation_url }'

        html = '<p>W celu powierdzenia subskrybcji newsletter unkot.pl '
        html += 'prosimy o odwiedzenie '
        html += f'<a href="{ activation_url }">linku aktywacyjnego</a>.</p>'
        send_mail(
            subject=subject,
            message=msg,
            html_message=html,
            from_email='kontakt@unkot.pl',
            recipient_list=[
                self.email,
            ],
            fail_silently=False,
        )
        self.activation_email_sent_ts = timezone.now()
        self.save()

    def activate(self):
        self.active = True
        self.save()
