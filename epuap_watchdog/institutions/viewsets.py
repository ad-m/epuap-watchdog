from rest_framework import viewsets

from .models import RESP, REGONError, REGON, JSTConnection, Institution, ESP
from .serializers import RESPSerializer, REGONSerializer, REGONErrorSerializer, JSTConnectionSerializer, \
    InstitutionSerializer, ESPSerializer


class InstitutionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Institution.objects.prefetch_related('esp_set', 'regon_data__regonerror_set').\
        select_related('jstconnection', 'regon_data', 'resp').all()
    serializer_class = InstitutionSerializer


class ESPViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ESP.objects.select_related('institution').all()
    serializer_class = ESPSerializer


class RESPViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RESP.objects.select_related('institution').all()
    serializer_class = RESPSerializer


class REGONViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = REGON.objects.prefetch_related('regonerror_set').select_related('institution').all()
    serializer_class = REGONSerializer


class REGONErrorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = REGONError.objects.select_related('regon').all()
    serializer_class = REGONErrorSerializer


class JSTConnectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = JSTConnection.objects.select_related('institution', 'jst').all()
    serializer_class = JSTConnectionSerializer
