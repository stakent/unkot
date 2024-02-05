from django.contrib import admin

from .models import Deed, DeedText, SearchIsap, SearchIsapResult


@admin.register(Deed)
class DeedAdmin(admin.ModelAdmin):
    pass


@admin.register(DeedText)
class DeedTextAdmin(admin.ModelAdmin):
    pass


@admin.register(SearchIsap)
class SearchIsapAdmin(admin.ModelAdmin):
    pass


@admin.register(SearchIsapResult)
class SearchIsapResultAdmin(admin.ModelAdmin):
    pass
