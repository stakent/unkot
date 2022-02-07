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
    return f"{ settings.ISAP_PDF_DIR }{ address[-3:] }/"


def get_deed_text_dir(address):
    return f"{ settings.ISAP_TEXT_DIR }{ address[-3:] }/"


class SearchIsap(models.Model):
    "SearchIsap stores an ISAP search: query, results, first_run_ts, last_run_ts"
    query = models.CharField(max_length=2000, default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_run_ts = models.DateTimeField(blank=True, null=True)
    last_run_ts = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = [['query', 'user']]

    def __str__(self):
        return self.query


class SearchIsapResult(models.Model):
    search = models.ForeignKey('SearchIsap', on_delete=models.CASCADE)
    first_run_ts = models.DateTimeField(blank=True, null=True)
    last_run_ts = models.DateTimeField(blank=True, null=True)
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

    def save(self, *args, **kwargs):
        '''On save, update timestamps'''
        try:
            now = kwargs['now']
        except KeyError:
            now = timezone.now()
        try:
            del kwargs['now']
        except KeyError:
            pass
        if not self.id:
            self.first_run_ts = now
        self.result_md5 = hashlib.md5(''.join(self.result).encode()).hexdigest()
        self.last_run_ts = now
        try:
            self.search.first_run_ts = min(self.search.first_run_ts, self.first_run_ts)
        except TypeError:
            self.search.first_run_ts = self.first_run_ts
        try:
            self.search.last_run_ts = max(self.search.last_run_ts, self.last_run_ts)
        except TypeError:
            self.search.last_run_ts = self.last_run_ts
        self.search.save()
        return super(SearchIsapResult, self).save(*args, **kwargs)


def save_search_result(query, addresses, user, now=None):
    ss, _ = SearchIsap.objects.get_or_create(
        query=query,
        user=user,
    )
    ssr, _ = SearchIsapResult.objects.get_or_create(search=ss, result=addresses)
    if now is not None:
        ssr.save(now=now)
    else:
        ssr.save()
