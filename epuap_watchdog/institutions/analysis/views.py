from braces.views import SelectRelatedMixin
from django.db.models import F, Count
from django.utils.translation import ugettext as _
from django.views.generic import ListView, TemplateView

from epuap_watchdog.institutions.models import Institution, ESP


class DivergentNameInstitution(ListView):
    model = Institution
    select_related = ['regon_data', 'resp']
    paginate_by = 50
    template_name = 'institutions/institution_diverge_name.html'

    def get_queryset(self):
        def normalize(name):
            return name.replace(' ' * 2, ' ').lower()

        return [x for x in self.model.objects.select_related('regon_data', 'resp').
            exclude(regon_data=None).
            exclude(regon_data__data=None).
            exclude(regon_data__name=F('resp__name')).iterator()
                if normalize(x.regon_data.data['nazwa']) != normalize(x.resp.data['name'])]


class NoLocationNameInstitutionView(SelectRelatedMixin, ListView):
    model = Institution
    select_related = ['regon_data', 'resp', 'jstconnection__jst', 'jstconnection']
    paginate_by = 50
    template_name = 'institutions/institution_no_location_name.html'

    def get_queryset(self):
        qs = super(NoLocationNameInstitutionView, self).get_queryset()
        for value in [' W ', ' w ', ' we ', ' WE ']:
            qs = qs.exclude(resp__name__contains=value)
        return qs


class NumeralStatView(TemplateView):
    template_name = 'institutions/institution_stat.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['no_regon'] = Institution.objects.filter(regon_data=None).count()
        context['no_jst'] = Institution.objects.filter(jstconnection=None).count()
        context['institution_count'] = Institution.objects.count()
        context['esp_count'] = ESP.objects.count()
        context['average_esp'] = context['esp_count'] / context['institution_count']
        return context


class MostCommonNamesView(ListView):
    template_name = 'institutions/institution_common_name.html'
    model = Institution
    paginate_by = 50
    CRITERIA_LIST = {'name': _("Own name"),
                     'resp__name': _("ePUAP name"),
                     'regon_data__name': _("REGON name")}

    def get_criteria(self):
        value = self.request.GET.get('criteria', 'name')
        return value if value in self.CRITERIA_LIST else 'name'

    def get_queryset(self):
        qs = super().get_queryset().values_list(self.get_criteria()).annotate(name_count=Count(self.get_criteria()))
        if self.get_criteria() == 'regon__data__name':
            qs = qs.exclude(regon__data=None).exclude(regon__data__data=None)
        return qs.exclude(name_count=1).order_by('-name_count')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['criteria_selected'] = self.get_criteria()
        context['criteria_list'] = self.CRITERIA_LIST
        return context


class FixedNamesView(ListView):
    template_name = 'institutions/fixed_names.html'
    model = Institution
    paginate_by = 50

    def get_queryset(self):
        return super().get_queryset().values_list('name').annotate(name_count=Count('name')). \
            exclude(name_count=1).order_by('-name_count')
