from django.conf.urls import url, include
from django.utils.translation import ugettext_lazy as _

from . import views

urlpatterns = [
    url(
        regex=_(r'^institution-(?P<epuap_id>[\w_-]+)/$'),
        view=views.InstitutionDetailView.as_view(),
        name='details'
    ),
    url(
        regex=_(r'^search_institution/$'),
        view=views.InstitutionSearchView.as_view(),
        name='search'
    ),
    url(
        regex=_(r'^region-(?P<pk>[\d]+)/$'),
        view=views.TERCView.as_view(),
        name='terc'
    ),
    url(_(r'^stats/'), include('epuap_watchdog.institutions.analysis.urls'), name='institution_stats'),
    url(
        regex=r'',
        view=views.HomeView.as_view(),
        name='home'
    ),
]
