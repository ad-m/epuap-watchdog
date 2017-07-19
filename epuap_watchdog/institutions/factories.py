# coding=utf-8
import datetime

import factory
import factory.fuzzy
from teryt_tree.factories import JednostkaAdministracyjnaFactory


class RESPFactory(factory.django.DjangoModelFactory):
    institution = factory.SubFactory("epuap_watchdog.institutions.factories.InstitutionFactory")
    name = factory.Sequence("resp-name-{0}".format)

    @factory.lazy_attribute_sequence
    def data(self, n):
        return {'adres': 'UL. WILEŃSKA {}'.format(n),
                'kod_pocztowy': "{0:02.0f}-{0:03.0f}".format(n),
                'miejscowosc': 'ŁÓDŹ',
                'name': self.name,
                'regon': n * 1000}

    class Meta:
        model = 'institutions.RESP'


class InstitutionFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence("institution-name-{0}".format)
    epuap_id = factory.Sequence("institution-epuap_id-{0}".format)
    regon = factory.Sequence("{0:014.0f}".format)
    active = factory.Sequence(lambda n: n % 2 == 0)

    class Meta:
        model = 'institutions.Institution'


class ESPFactory(factory.django.DjangoModelFactory):
    institution = factory.SubFactory("epuap_watchdog.institutions.factories.InstitutionFactory")
    name = factory.Sequence("esp-name-{0}".format)
    active = factory.Sequence(lambda n: n % 2 == 0)

    class Meta:
        model = 'institutions.ESP'


class REGONFactory(factory.django.DjangoModelFactory):
    institution = factory.SubFactory("epuap_watchdog.institutions.factories.InstitutionFactory")
    name = factory.Sequence("regon-name-{0}".format)
    regon = factory.Sequence("{0:014.0f}".format)

    @factory.lazy_attribute_sequence
    def data(self, n):
        return {'adkorgmina_nazwa': '',
                'adkorgmina_symbol': '',
                'adkorkodpocztowy': '',
                'adkorkraj_nazwa': '',
                'adkorkraj_symbol': '',
                'adkormiejscowosc_nazwa': '',
                'adkormiejscowosc_symbol': '',
                'adkormiejscowoscipoczty_symbol': '',
                'adkormiejscowoscpoczty_nazwa': '',
                'adkornazwapodmiotudokorespondencji': '',
                'adkornietypowemiejscelokalizacji': '',
                'adkornumerlokalu': '',
                'adkornumernieruchomosci': '',
                'adkorpowiat_nazwa': '',
                'adkorpowiat_symbol': '',
                'adkorulica_nazwa': '',
                'adkorulica_symbol': '',
                'adkorwojewodztwo_nazwa': '',
                'adkorwojewodztwo_symbol': '',
                'adresemail': 'zlobek28@o2.pl',
                'adresemail2': '',
                'adresstronyinternetowej': '',
                'adsiedzgmina_nazwa': 'Kraków-Podgórze',
                'adsiedzgmina_symbol': '049',
                'adsiedzkodpocztowy': '30868',
                'adsiedzkraj_nazwa': 'POLSKA',
                'adsiedzkraj_symbol': 'PL',
                'adsiedzmiejscowosc_nazwa': 'Kraków',
                'adsiedzmiejscowosc_symbol': '0950960',
                'adsiedzmiejscowoscpoczty_nazwa': 'Kraków',
                'adsiedzmiejscowoscpoczty_symbol': '0950960',
                'adsiedznietypowemiejscelokalizacji': '',
                'adsiedznumerlokalu': '',
                'adsiedznumernieruchomosci': '21',
                'adsiedzpowiat_nazwa': 'm. Kraków',
                'adsiedzpowiat_symbol': '61',
                'adsiedzulica_nazwa': 'ul. Jana Kurczaba',
                'adsiedzulica_symbol': '10434',
                'adsiedzwojewodztwo_nazwa': 'MAŁOPOLSKIE',
                'adsiedzwojewodztwo_symbol': '12',
                'datapowstania': '2001-02-02',
                'datarozpoczeciadzialalnosci': '2011-01-01',
                'dataskresleniazregon': '',
                'datawpisudoregon': '2011-01-04',
                'datawznowieniadzialalnosci': '',
                'datazaistnieniazmiany': '2011-01-04',
                'datazakonczeniadzialalnosci': '',
                'datazawieszeniadzialalnosci': '',
                'formafinansowania_nazwa': 'JEDNOSTKA BUDŻETOWA',
                'formafinansowania_symbol': '2',
                'formawlasnosci_nazwa': 'WŁASNOŚĆ JEDNOSTEK SAMORZĄDU TERYTORIALNEGO LUB SAMORZĄDOWYCH OSÓB PRAWNYCH',
                'formawlasnosci_symbol': '113',
                'jednosteklokalnych': '0',
                'nazwa': 'ŻŁOBEK SAMORZADOWY NR 28',
                'nazwaskrocona': '',
                'nip': "{0:010.0f}".format(n),
                'numerfaksu': '0123456789',
                'numertelefonu': '0123456789',
                'numerwewnetrznytelefonu': '',
                'numerwrejestrzeewidencji': '1200076',
                'organrejestrowy_nazwa': 'WOJEWODA MAŁOPOLSKI',
                'organrejestrowy_symbol': '010120000',
                'organzalozycielski_nazwa': 'WOJEWODA MAŁOPOLSKI',
                'organzalozycielski_symbol': '200120000',
                'podstawowaformaprawna_nazwa': 'JEDNOSTKA ORGANIZACYJNA NIEMAJĄCA OSOBOWOŚCI PRAWNEJ',
                'podstawowaformaprawna_symbol': '2',
                'regon14': self.regon,
                'rodzajrejestruewidencji_nazwa': 'REJESTR ZAKŁADÓW OPIEKI ZDROWOTNEJ',
                'rodzajrejestruewidencji_symbol': '029',
                'szczegolnaformaprawna_nazwa': 'GMINNE SAMORZĄDOWE JEDNOSTKI ORGANIZACYJNE',
                'szczegolnaformaprawna_symbol': '429'}

    class Meta:
        model = 'institutions.REGON'


class JSTConnectionFactory(factory.django.DjangoModelFactory):
    institution = factory.SubFactory("epuap_watchdog.institutions.factories.InstitutionFactory")
    jst = factory.SubFactory("teryt_tree.factories.JednostkaAdministracyjnaFactory")

    class Meta:
        model = 'institutions.JSTConnection'


class REGONErrorFactory(factory.django.DjangoModelFactory):
    regon = factory.SubFactory("epuap_watchdog.institutions.factories.REGONFactory")
    exception = factory.Sequence("regonerror-exception-{0}".format)

    class Meta:
        model = 'institutions.REGONError'


class JSTConnectionFactory(factory.django.DjangoModelFactory):
    institution = factory.SubFactory("epuap_watchdog.institutions.factories.InstitutionFactory")
    jst = factory.SubFactory(JednostkaAdministracyjnaFactory)

    class Meta:
        model = 'institutions.JSTConnection'
