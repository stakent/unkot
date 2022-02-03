import secrets

from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Subscriber


class NewsletterTest(TestCase):
    def test_create_subscriber(self):
        email = 'test@example.com'
        s = Subscriber.objects.create(email=email)
        s.activation_token = secrets.token_urlsafe()
        self.assertFalse(s.active)
        self.assertNotEqual(s.activation_token, '')

    def test_send_activation_email(self):
        email = 'test2@example.com'
        s = Subscriber.objects.create(email=email)

        ts1 = timezone.now()

        s.send_activation_email()

        ts2 = timezone.now()
        self.assertIsNotNone(s.activation_email_sent_ts)
        self.assertLess(ts1, s.activation_email_sent_ts)
        self.assertGreater(ts2, s.activation_email_sent_ts)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('unkot.pl', mail.outbox[0].subject)
        self.assertIsNotNone(s.activation_token)
        self.assertNotEqual(s.activation_token, "")
        self.assertIn(s.activation_token, mail.outbox[0].body)
        activation_href = '<a href="'
        self.assertIn(activation_href, mail.outbox[0].message().as_string())

    def test_activate_subscription(self):
        email = 'test_as@example.com'
        s = Subscriber.objects.create(
            email=email, activation_token=secrets.token_urlsafe()
        )
        s.save()

        s2 = Subscriber.objects.get(email=email)
        self.assertFalse(s2.active)

        c = Client()
        url = reverse('newsletter_activate', kwargs={'token': s2.activation_token})
        resp = c.get(url)

        self.assertEqual(resp.status_code, 200)
        s3 = Subscriber.objects.get(email=email)
        self.assertTrue(s3.active)

    def test_unsubscribe(self):
        email = 'test_us@example.com'
        s = Subscriber.objects.create(
            email=email, activation_token=secrets.token_urlsafe()
        )
        s.active = True
        s.save()

        c = Client()
        url = reverse('newsletter_unsubscribe', kwargs={'email': email})
        resp = c.get(url)

        self.assertEqual(resp.status_code, 200)
        s2 = Subscriber.objects.get(email=email)
        self.assertFalse(s2.active)
