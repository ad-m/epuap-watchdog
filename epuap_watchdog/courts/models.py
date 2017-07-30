import reversion
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from model_utils.models import TimeStampedModel

from epuap_watchdog.institutions.models import Institution, REGON


class CourtQuerySet(models.QuerySet):
    pass


@reversion.register()
@python_2_unicode_compatible
class Court(TimeStampedModel):
    parent = models.ForeignKey('self', null=True, blank=True)
    name = models.CharField(verbose_name=_("Name"), max_length=100)
    district = models.CharField(verbose_name=_("District name"), blank=True, max_length=100)
    appeal = models.CharField(verbose_name=_("Appeal name"), blank=True, max_length=100)
    street = models.CharField(verbose_name=_("Street"), max_length=100)
    postcode = models.CharField(verbose_name=_("Post code"), max_length=6)
    phone = models.CharField(verbose_name=_("Telephone"), max_length=100)
    fax = models.CharField(verbose_name=_("Telephone"), max_length=100)
    email = models.EmailField(verbose_name=_("E-mail"))
    objects = CourtQuerySet.as_manager()
    active = models.BooleanField(default=True, verbose_name=_("Is court active?"))

    class Meta:
        verbose_name = _("Court")
        verbose_name_plural = _("Courts")
        ordering = ['created', ]

    def __str__(self):
        return self.name


@reversion.register()
@python_2_unicode_compatible
class REGONGuest(TimeStampedModel):
    regon = models.ForeignKey(REGON)
    court = models.OneToOneField(Court)

