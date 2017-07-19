from rest_framework import serializers
from teryt_tree.rest_framework_ext.serializers import JednostkaAdministracyjnaSerializer

from .models import RESP, REGONError, REGON, JSTConnection, Institution, ESP


class RESPSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RESP
        fields = ['id', 'created', 'modified', 'institution_id', 'name', 'data']


class REGONErrorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = REGONError
        fields = ['id', 'created', 'modified', 'regon_id', 'exception']


class REGONSerializer(serializers.HyperlinkedModelSerializer):
    regonerror_set = REGONErrorSerializer(many=True)

    class Meta:
        model = REGON
        fields = ['id', 'created', 'modified', 'institution_id', 'name', 'regon', 'regonerror_set', 'data']


class JSTConnectionSerializer(serializers.HyperlinkedModelSerializer):
    # jst = JednostkaAdministracyjnaSerializer()

    class Meta:
        model = JSTConnection
        fields = ['id', 'created', 'modified', 'institution_id', 'jst_id']


class ESPSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ESP
        fields = ['id', 'created', 'modified', 'institution_id', 'name', 'active']


class InstitutionSerializer(serializers.HyperlinkedModelSerializer):
    resp = RESPSerializer()
    regon_data = REGONSerializer()
    jstconnection = JSTConnectionSerializer()
    esp_set = ESPSerializer(many=True)

    class Meta:
        model = Institution
        fields = ['id', 'created', 'modified', 'name', 'epuap_id', 'regon', 'active',
                  'esp_set', 'jstconnection', 'regon_data', 'resp']
