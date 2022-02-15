import hashlib
import io
from datetime import date, datetime

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.db import models
from django.urls import reverse
from django.utils import timezone

from unkot.users.models import User

NO_DATE_PROVIDED = date(1, 1, 1)
NO_DATETIME_PROVIDED = datetime(1, 1, 1, 0, 0, tzinfo=timezone.utc)


class Deed(models.Model):
    "Deed"

    address = models.CharField(primary_key=True, max_length=200, default="")
    publisher = models.CharField(max_length=200, default="")
    year = models.IntegerField(default=0)
    volume = models.IntegerField(default=0)
    pos = models.IntegerField(default=0)
    deed_type = models.CharField(max_length=200, default="")
    title = models.CharField(max_length=2000, default="")
    status = models.CharField(max_length=200, default="")
    display_address = models.CharField(max_length=200, default="")
    promulgation = models.DateField(blank=True, default=NO_DATE_PROVIDED)
    announcement_date = models.DateField(blank=True, default=NO_DATE_PROVIDED)
    change_date = models.DateTimeField(blank=True, default=NO_DATETIME_PROVIDED)
    eli = models.CharField(max_length=200, default="")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('deed_detail', kwargs={'pk': self.pk})


class DeedText(models.Model):
    deed = models.ForeignKey(Deed, on_delete=models.CASCADE)
    change_date = models.DateTimeField(blank=True, default=NO_DATETIME_PROVIDED)
    seq = models.IntegerField(default=0)
    text = models.TextField(default="")
    search_vector = SearchVectorField(null=True)

    class Meta:
        indexes = (GinIndex(fields=["search_vector"]),)

    def __str__(self):
        return f'{ self.deed.title} { self.seq }'


def save_deed_text(address, change_date, text):
    """Save deed text in chunks and update search vectors."""
    max_size = 500_000  # approx. size of the deed text part in db
    lines = text.splitlines(keepends=True)
    part = io.StringIO()
    seq = 1
    curr_size = 0
    for line in lines:
        part.write(line)
        curr_size = curr_size + len(line)
        if curr_size > max_size:
            dt, _ = DeedText.objects.get_or_create(deed_id=address, seq=seq)
            dt.change_date = change_date
            dt.text = part.getvalue()
            dt.save()
            dt.search_vector = SearchVector("text", config="polish")
            dt.save()
            part = io.StringIO()
            seq = seq + 1
            curr_size = 0
    if curr_size > 0:
        dt, _ = DeedText.objects.get_or_create(deed_id=address, seq=seq)
        dt.text = part.getvalue()
        dt.save()
        dt.search_vector = SearchVector("text", config="polish")
        dt.save()
    return


def load_deed_text(address):
    dts = DeedText.objects.filter(deed_id=address).order_by("seq")
    text = io.StringIO()
    for dt in dts:
        text.write(dt.text)
    return text.getvalue()


def get_deed_pdf_dir(address):
    # WDU20220000013
    # 01234567890123
    return f"{ settings.ISAP_PDF_DIR }{ address[3:7] }/"


def get_deed_text_dir(address):
    return f"{ settings.ISAP_TEXT_DIR }{ address[3:7] }/"


class SearchIsap(models.Model):
    "SearchIsap stores an ISAP search: query, results, first_run_ts, last_run_ts"
    query = models.CharField(max_length=2000, default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_run_ts = models.DateTimeField(blank=True, null=True)
    last_run_ts = models.DateTimeField(
        blank=True, null=True, default=datetime(1, 1, 1, tzinfo=timezone.utc)
    )
    subscribed = models.BooleanField(default=False)

    class Meta:
        unique_together = [['query', 'user']]

    def __str__(self):
        return f'"{ self.query }" { self.user.name }'


class SearchIsapResult(models.Model):
    @classmethod
    def get_result_md5(_, result):
        return hashlib.md5(''.join(sorted(result)).encode()).hexdigest()

    search = models.ForeignKey('SearchIsap', on_delete=models.CASCADE)
    first_run_ts = models.DateTimeField(default=NO_DATETIME_PROVIDED)
    last_run_ts = models.DateTimeField(default=NO_DATETIME_PROVIDED)
    result = ArrayField(models.CharField(max_length=200), blank=True, default=list)
    # enforcing unique_together by postgresql on (query, result) causes
    # exceeding of pg limitations for the size of indexed values
    # so we use md5 hash of result
    result_md5 = models.CharField(max_length=32, editable=False, default='')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['search', 'result_md5'], name='search_isap_result_md5_uniq'
            ),
        ]

    def __str__(self):
        return f'"{ str(self.search) } { self.first_run_ts }'

    def save(self, *args, **kwargs):
        '''On save, update result hash'''
        self.result_md5 = self.get_result_md5(self.result)
        return super(SearchIsapResult, self).save(*args, **kwargs)


def save_search_result(query, addresses, user, now):
    if now is None:
        raise ValueError('save_search_result: parameter now is None')
    ss, created = SearchIsap.objects.get_or_create(
        query=query,
        user=user,
    )
    if created:
        ss.first_run_ts = now
    ss.last_run_ts = now
    ss.save()

    ssr, created = SearchIsapResult.objects.get_or_create(
        search=ss,
        result_md5=SearchIsapResult.get_result_md5(addresses),
    )
    if created:
        ssr.first_run_ts = now
    ssr.last_run_ts = now
    ssr.result = addresses
    ssr.save()
