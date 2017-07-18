from django.conf.urls import url
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
    url(
        regex=_(r'^diverge-name'),
        view=views.DivergentNameInstitution.as_view(),
        name='diverge-name'
    ),
    url(
        regex=_(r'^no-location-name'),
        view=views.NoLocationNameInstitutionView.as_view(),
        name='no-location-name'
    ),
    url(
        regex=_(r'^stats'),
        view=views.NumeralStatView.as_view(),
        name='numeral-stat'
    ),

    url(
        regex=r'',
        view=views.HomeView.as_view(),
        name='home'
    ),
]
