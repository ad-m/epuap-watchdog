import reversion
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel
from reversion.models import Version
from teryt_tree.models import JednostkaAdministracyjna

from epuap_watchdog.users.models import User


class InstitutionQuerySet(models.QuerySet):
    pass


@reversion.register()
@python_2_unicode_compatible
class Institution(TimeStampedModel):
    name = models.CharField(verbose_name=_("Name"), max_length=200)
    slug = models.SlugField()
    epuap_id = models.CharField(verbose_name=_("ePUAP ID"), max_length=100,
                                db_index=True, unique=True,
                                help_text=_("Basic Institution ID in ePUAP"))
    regon = models.CharField(verbose_name=_("REGON  number"), max_length=20, db_index=True, null=True)
    address = models.CharField(max_length=100, verbose_name=_("Address"), null=True)
    postal_code = models.CharField(max_length=6, null=True)
    city = models.CharField(max_length=100, null=True)
    active = models.BooleanField(verbose_name=_("Active status"), help_text=_("Is the institution active?"), default=True)
    versions = GenericRelation(Version)

    objects = InstitutionQuerySet.as_manager()

    class Meta:
        verbose_name = _("Institution")
        verbose_name_plural = _("Institutions")
        ordering = ['created', ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('institutions:details', kwargs={'slug': self.slug})


class ESPQuerySet(models.QuerySet):
    pass


class ESP(TimeStampedModel):
    institution = models.ForeignKey(Institution, verbose_name=_("Institution"))
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    active = models.BooleanField(verbose_name=_("Active status"), help_text=_("Is the ESP active?"), default=True)

    def uri(self):
        return "/{}/{}".format(self.institution.epuap_id, self.name)

    class Meta:
        verbose_name = _("ESP")
        verbose_name_plural = _("ESPs")
        ordering = ['created']


@reversion.register()
@python_2_unicode_compatible
class REGON(TimeStampedModel):
    institution = models.OneToOneField(Institution, verbose_name=_("Institution"), related_name="regon_data")
    regon = models.CharField(verbose_name=_("REGON  number"), max_length=20, db_index=True, null=True)
    data = JSONField(verbose_name=_("Response data"), help_text=_("Data for database search results REGON BIP1"), null=True, blank=True)

    def __str__(self):
        return "REGON {} at {}".format(self.regon, self.created.strftime("%Y-%m-%d %H-%M"))

    class Meta:
        verbose_name = _("REGON")
        verbose_name_plural = _("REGONs")
        ordering = ['created']


@reversion.register()
@python_2_unicode_compatible
class REGONError(TimeStampedModel):
    regon = models.OneToOneField(REGON, verbose_name=_("REGON"))
    exception = models.CharField(max_length=200)


@reversion.register()
class JSTConnection(TimeStampedModel):
    institution = models.OneToOneField(Institution, verbose_name=_("Institution"))
    jst = models.ForeignKey(JednostkaAdministracyjna, verbose_name=_("Administration division unit"))

    class Meta:
        verbose_name = _("JSTConnection")
        verbose_name_plural = _("JSTConnections")
        ordering = ['created']
