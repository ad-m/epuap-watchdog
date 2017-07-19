from test_plus.test import TestCase
from atom.ext.rest_framework.mixins import ViewSetTestCaseMixin
from .models import RESP, REGONError, REGON, JSTConnection, Institution, ESP
from .factories import RESPFactory, REGONFactory, REGONErrorFactory, JSTConnectionFactory, InstitutionFactory, ESPFactory

GLOBAL_QUERY_LIMIT = 20

class InstitutionViewSetTestCase(ViewSetTestCaseMixin, TestCase):
    QUERY_LIMIT = GLOBAL_QUERY_LIMIT
    DETAIL_VIEW = 'institution-detail'
    LIST_VIEW = 'institution-list'
    FACTORY_CLS = InstitutionFactory


class ESPViewSetTestCase(ViewSetTestCaseMixin, TestCase):
    QUERY_LIMIT = GLOBAL_QUERY_LIMIT
    DETAIL_VIEW = 'esp-detail'
    LIST_VIEW = 'esp-list'
    FACTORY_CLS = ESPFactory


class RESPViewSetTestCase(ViewSetTestCaseMixin, TestCase):
    QUERY_LIMIT = GLOBAL_QUERY_LIMIT
    DETAIL_VIEW = 'resp-detail'
    LIST_VIEW = 'resp-list'
    FACTORY_CLS = RESPFactory


class REGONViewSetTestCase(ViewSetTestCaseMixin, TestCase):
    QUERY_LIMIT = GLOBAL_QUERY_LIMIT
    DETAIL_VIEW = 'regon-detail'
    LIST_VIEW = 'regon-list'
    FACTORY_CLS = REGONFactory


class JSTConnectionViewSetTestCase(ViewSetTestCaseMixin, TestCase):
    QUERY_LIMIT = GLOBAL_QUERY_LIMIT
    DETAIL_VIEW = 'jstconnection-detail'
    LIST_VIEW = 'jstconnection-list'
    FACTORY_CLS = JSTConnectionFactory
