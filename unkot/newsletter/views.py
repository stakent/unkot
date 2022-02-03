from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from .forms import SubscribeForm
from .models import Subscriber


def subscribe(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SubscribeForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            email = form.cleaned_data['email']
            # print(f'==== newsletter subscribe: { email }')
            s, _ = Subscriber.objects.get_or_create(email=email)
            s.send_activation_email()
            s.save()

            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('newsletter_activation_email_sent'))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SubscribeForm()

    return render(request, "newsletter/subscribe.html", {'form': form})


def activation_email_sent(request):
    return render(request, "newsletter/activation_email_sent.html")


def activate(request, token):
    s = Subscriber.objects.get(activation_token=token)
    s.active = True
    s.save()
    return render(request, "newsletter/subscription_activated.html")


def subscriber(request, email):
    pass


def unsubscribe(request, email):
    s = Subscriber.objects.get(email=email)
    s.active = False
    s.deactivation_ts = timezone.now()
    s.save()
    return render(request, "newsletter/unsubscribed.html")
