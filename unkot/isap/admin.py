from django.contrib import admin
from .models import Deed, DeedText, SearchIsap, SearchIsapResult


class DeedAdmin(admin.ModelAdmin):
    pass


admin.site.register(Deed, DeedAdmin)


class DeedTextAdmin(admin.ModelAdmin):
    pass


admin.site.register(DeedText, DeedTextAdmin)


class SearchIsapAdmin(admin.ModelAdmin):
    pass


admin.site.register(SearchIsap, SearchIsapAdmin)


class SearchIsapResultAdmin(admin.ModelAdmin):
    pass


admin.site.register(SearchIsapResult, SearchIsapResultAdmin)
