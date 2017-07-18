from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views

urlpatterns = [
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
        regex=_(r'^stats$'),
        view=views.NumeralStatView.as_view(),
        name='numeral-stat'
    ),
    url(
        regex=_(r'^name-counts'),
        view=views.MostCommonNamesView.as_view(),
        name='name-counts'
    ),
]
