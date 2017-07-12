from django.contrib import admin

# Register your models here.
from reversion.admin import VersionAdmin

from epuap_watchdog.institutions.models import ESP, Institution


class ESPInline(admin.TabularInline):
    '''
        Tabular Inline View for ESP
    '''
    model = ESP


class InstitutionAdmin(VersionAdmin):
    '''
        Admin View for Institution
    '''
    list_display = ('name', 'epuap_id', 'regon', 'address', 'teryt', 'postal_code', 'city','version_count');
    inlines = [
        ESPInline,
    ]
    readonly_fields = ('epuap_id', 'slug')
    search_fields = ('name', 'regon')

    def version_count(self, obj):
        return obj.versions.all().count()

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('versions')


admin.site.register(Institution, InstitutionAdmin)
