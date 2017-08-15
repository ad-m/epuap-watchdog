from django.contrib.postgres.fields import JSONField
from django.db import models

# Create your models here.
from model_utils.models import TimeStampedModel
from teryt_tree.models import JednostkaAdministracyjna, SIMC

from epuap_watchdog.institutions.models import REGON


class CityHall(TimeStampedModel):
    original_name = models.CharField(max_length=100)
    original_pk = models.IntegerField(db_index=True, unique=True)
    original_terc = models.ForeignKey(JednostkaAdministracyjna, null=True)
    detected_name = models.CharField(max_length=100)
    detected_regon = models.ForeignKey(REGON, null=True)

    extra = JSONField(blank=True, null=True)
