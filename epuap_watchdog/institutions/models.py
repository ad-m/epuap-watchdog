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
    def area(self, jst):
        return self.filter(jstconnection__jst__tree_id=jst.tree_id,
                           jstconnection__jst__lft__range=(jst.lft, jst.rght))

    def with_jst(self):
        return self.select_related('jstconnection__jst')


@reversion.register()
@python_2_unicode_compatible
class Institution(TimeStampedModel):
    name = models.CharField(verbose_name=_("Name"), max_length=200)
    epuap_id = models.CharField(verbose_name=_("ePUAP ID"), max_length=100,
                                db_index=True, unique=True,
                                help_text=_("Basic Institution ID in ePUAP"))
    regon = models.CharField(verbose_name=_("REGON  number"), max_length=20, db_index=True, null=True)
    active = models.BooleanField(verbose_name=_("Active status"), help_text=_("Is the institution active?"),
                                 default=True)
    versions = GenericRelation(Version)
    objects = InstitutionQuerySet.as_manager()

    def jst(self):
        return self.jstconnection.jst if hasattr(self, 'jstconnection') else None

    def is_located_in_name(self):
        return any(v in self.name.lower() for v in [' w ', ' we'])

    def esp_generator(self):
        return ({'name': "/%s/%s " % (self.epuap_id, esp.name), 'active': esp.active}
                for esp in self.esp_set.all())


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

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("ESP")
        verbose_name_plural = _("ESPs")
        ordering = ['created']
        unique_together = [['institution', 'name', ]]


@reversion.register()
@python_2_unicode_compatible
class RESP(TimeStampedModel):
    institution = models.OneToOneField(Institution)
    name = models.CharField(max_length=200, db_index=True, verbose_name=_("Name"))
    data = JSONField(verbose_name=_("XML data"),
                     help_text=_("Data from load RESP.xml"), null=True, blank=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.data:
            self.name = self.data.get('name', '')
        return super().save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name = _("RESP")
        verbose_name_plural = _("RESPs")
        ordering = ['created']


@reversion.register()
@python_2_unicode_compatible
class REGON(TimeStampedModel):
    institution = models.OneToOneField(Institution, verbose_name=_("Institution"), related_name="regon_data")
    name = models.CharField(max_length=200, db_index=True, verbose_name=_("Name"))
    regon = models.CharField(verbose_name=_("REGON  number"), max_length=20, db_index=True, null=True)
    data = JSONField(verbose_name=_("Response data"), help_text=_("Data for database search results REGON BIP1"),
                     null=True, blank=True)
    versions = GenericRelation(Version)

    def __str__(self):
        return "REGON {} at {}".format(self.regon, self.created.strftime("%Y-%m-%d %H-%M"))

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.data:
            self.name = self.data.get('nazwa', '')
        return super().save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name = _("REGON")
        verbose_name_plural = _("REGONs")
        ordering = ['created']


@reversion.register()
@python_2_unicode_compatible
class REGONError(TimeStampedModel):
    regon = models.ForeignKey(REGON, verbose_name=_("REGON"))
    exception = models.CharField(max_length=200)
    versions = GenericRelation(Version)


@reversion.register()
class JSTConnection(TimeStampedModel):
    institution = models.OneToOneField(Institution, verbose_name=_("Institution"))
    jst = models.ForeignKey(JednostkaAdministracyjna, verbose_name=_("Administration division unit"))
    versions = GenericRelation(Version)

    class Meta:
        verbose_name = _("JSTConnection")
        verbose_name_plural = _("JSTConnections")
        ordering = ['created']
