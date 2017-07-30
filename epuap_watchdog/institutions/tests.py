from test_plus.test import TestCase
from unittest import TestCase as FastTestCase

from atom.ext.rest_framework.mixins import ViewSetTestCaseMixin

from epuap_watchdog.institutions.utils import normalize, normalize_regon
from .factories import RESPFactory, REGONFactory, JSTConnectionFactory, InstitutionFactory, ESPFactory

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


class NormalizeNameTest(FastTestCase):
    rules = (('ŻŁOBEK SAMORZADOWY NR 28',
              'Żłobek samorządowy nr 28'),

             ('ŻŁOBEK POMNIK MATKI POLKI',
              'Żłobek Pomnik Matki Polki'),

             ('ŻŁOBEK NR 9 W OPOLU',
              'Żłobek nr 9 w Opolu'),

             ('I LICEUM OGÓLNOKSZTAŁCĄCE IM. KRÓLA KAZIMIERZA WIELKIEGO W OLKUSZU',
              'I Liceum Ogólnokształcące im. Króla Kazimierza Wielkiego w Olkuszu'),

             ('GMINNY OŚRODEK POMOCY SPOŁECZNEJ W WODYNIACH',
              'Gminny Ośrodek Pomocy Społecznej w Wodyniach'
              ),

             ('ZARZĄD DRÓG I UTRZYMANIA MIASTA',
              'Zarząd Dróg i Utrzymania Miasta'),

             ('KOMENDA WOJEWÓDZKA POLICJI WE WROCŁAWIU',
              'Komenda Wojewódzka Policji we Wrocławiu'),

             ('ZESPÓŁ SZKOLNO -  PRZEDSZKOLNY NR 3 W KOŚCIERZYNIE',
              'Zespół Szkolno - Przedszkolny nr 3 w Kościerzynie'),

             ('ZESPÓŁ SZKÓŁ PONADGIMNAZJALNYCH NR 2 IM. PAPIEŻA  JANA PAWŁA II',
              'Zespół Szkół Ponadgimnazjalnych nr 2 im. Papieża Jana Pawła II'),

             ('ZESPÓŁ SZKÓŁ IM.OJCA ŚWIĘTEGO JANA PAWŁA II W NIEPOŁOMICACH',
              'Zespół Szkół im. Ojca Świętego Jana Pawła II w Niepołomicach'),

             ('PAŃSTWOWA SZKOŁA MUZYCZNA I I II ST. W PABIANICACH',
              'Państwowa Szkoła Muzyczna I i II St. w Pabianicach'),

             ('XXXIII LICEUM OGÓLNOKSZTAŁCĄCE IM. ARMII KRAJOWEJ',
              'XXXIII Liceum Ogólnokształcące im. Armii Krajowej'),

            )

    def test_expected_result(self):
        for i, (source_name, expected_name) in enumerate(self.rules):
            self.assertEqual(normalize(source_name), expected_name, "Fail test no. {}".format(i + 1))


class NormalizeRegonTest(FastTestCase):
    def test_excpected_result(self):
        self.assertEqual(normalize_regon('00068362500000'), '000683625')
        self.assertEqual(normalize_regon('000683625'), '000683625')
        self.assertEqual(normalize_regon('00068362500001'), '00068362500001')
        self.assertEqual(normalize_regon('000683625-00001'), '00068362500001')
        self.assertEqual(normalize_regon('000683625-00000'), '000683625')
        self.assertEqual(normalize_regon(None), None)


