from itertools import islice

from braces.views import SelectRelatedMixin
from cached_property import cached_property
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from teryt_tree.models import JednostkaAdministracyjna

from epuap_watchdog.institutions.models import Institution


class HomeView(ListView):
    model = JednostkaAdministracyjna
    template_name = 'institutions/home.html'

    def get_queryset(self):
        return super(HomeView, self).get_queryset().voivodeship()


class TERCView(SelectRelatedMixin, ListView):
    model = Institution
    select_related = ['jstconnection__jst', ]
    template_name = 'institutions/institution_terc.html'
    paginate_by = 50

    def get_queryset(self):
        return super(TERCView, self).get_queryset().area(jst=self.object)

    @cached_property
    def object(self):
        return get_object_or_404(JednostkaAdministracyjna, id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        kwargs['object'] = self.object
        return super().get_context_data(**kwargs)


class InstitutionSearchView(SelectRelatedMixin, ListView):
    model = Institution
    paginate_by = 50
    select_related = ['jstconnection__jst']
    template_name_suffix = '_search'

    def get_query(self):
        return self.request.GET.get('q', 'ministerstwo cyfryzacji')

    def get_queryset(self):
        qs = super(InstitutionSearchView, self).get_queryset()
        return qs.filter(Q(name__icontains=self.get_query()) |
                         Q(resp__name__icontains=self.get_query()) |
                         Q(regon_data__name__icontains=self.get_query()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.get_query()
        return context


class InstitutionDetailView(SelectRelatedMixin, DetailView):
    model = Institution
    select_related = ['regon_data', 'resp', 'jstconnection__jst', 'jstconnection__jst__parent']
    slug_field = 'epuap_id'
    slug_url_kwarg = 'epuap_id'

    def get_near_queryset(self, ids, jst):
        return Institution.objects.exclude(pk__in=ids).area(jst).with_jst().order_by('jstconnection__jst_id').all()

    def get_near_institution(self, jst):
        if not jst:
            return
        ids = [self.object.pk]
        for institution in self.get_near_queryset(ids, jst)[:10]:
            ids.append(institution.id)
            yield institution
        for institution in self.get_near_queryset(ids, jst.parent)[:10 - len(ids) + 1]:
            ids.append(institution.id)
            yield institution

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['near_institution'] = islice(self.get_near_institution(self.object.jst()), 10)
        return context
