from django.contrib import admin
# Register your models here.
from reversion.admin import VersionAdmin

from epuap_watchdog.institutions.models import ESP, Institution, REGONError, REGON


class ESPInline(admin.TabularInline):
    '''
        Tabular Inline View for ESP
    '''
    model = ESP


class InstitutionAdmin(VersionAdmin):
    '''
        Admin View for Institution
    '''
    list_display = ('epuap_id', 'name',  'regon', 'version_count',
                    'created', 'modified')
    inlines = [
        ESPInline,
    ]
    readonly_fields = ('epuap_id', )
    search_fields = ('name', 'regon')

    def version_count(self, obj):
        return obj.versions.all().count()

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('versions')


admin.site.register(Institution, InstitutionAdmin)


class REGONErrorInline(admin.StackedInline):
    '''
        Stacked Inline View for REGONError
    '''
    model = REGONError


class REGONAdmin(VersionAdmin):
    '''
        Admin View for REGON
    '''
    list_display = ('regon', 'institution', 'version_count', 'created', 'modified')
    inlines = [
        REGONErrorInline,
    ]
    search_fields = ('regon', 'institution__name')

    def version_count(self, obj):
        return obj.versions.all().count()

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('versions')

admin.site.register(REGON, REGONAdmin)
