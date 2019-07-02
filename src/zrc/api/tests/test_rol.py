from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.constants import RolTypes
from vng_api_common.tests import (
    JWTAuthMixin, TypeCheckMixin, get_operation_url, get_validation_errors
)

from zrc.datamodel.models import (
    NatuurlijkPersoon, NietNatuurlijkPersoon, Rol, Vestiging
)
from zrc.datamodel.tests.factories import RolFactory, ZaakFactory

BETROKKENE = 'http://www.zamora-silva.org/api/betrokkene/8768c581-2817-4fe5-933d-37af92d819dd'


class US45TestCase(JWTAuthMixin, TypeCheckMixin, APITestCase):

    heeft_alle_autorisaties = True

    @freeze_time("2018-01-01")
    def test_read_rol_np(self):
        zaak = ZaakFactory.create()
        rol = RolFactory.create(
            zaak=zaak,
            betrokkene_type=RolTypes.natuurlijk_persoon,
            betrokkene='http://www.zamora-silva.org/api/betrokkene/8768c581-2817-4fe5-933d-37af92d819dd',
            rolomschrijving='Beslisser'
        )
        NatuurlijkPersoon.objects.create(
            rol=rol,
            anp_identificatie='12345',
            inp_a_nummer='1234567890'
        )
        zaak_url = get_operation_url('zaak_read', uuid=zaak.uuid)
        url = get_operation_url('rol_read', uuid=rol.uuid)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(
            data,
            {
                'url': f'http://testserver{url}',
                'zaak': f'http://testserver{zaak_url}',
                'betrokkene': BETROKKENE,
                'betrokkeneType': RolTypes.natuurlijk_persoon,
                'rolomschrijving': 'Beslisser',
                'roltoelichting': '',
                'registratiedatum': '2018-01-01T00:00:00Z',
                'betrokkeneIdentificatie': {
                    'inpBsn': '',
                    'anpIdentificatie': '12345',
                    'inpA_nummer': '1234567890',
                    'geslachtsnaam': '',
                    'voorvoegselGeslachtsnaam': '',
                    'voorletters': '',
                    'voornamen': '',
                    'geslachtsaanduiding': '',
                    'geboortedatum': '',
                    'verblijfsadres': '',
                    'subVerblijfBuitenland': ''
                }
            }
        )

    @freeze_time("2018-01-01")
    def test_read_rol_nnp(self):
        zaak = ZaakFactory.create()
        rol = RolFactory.create(
            zaak=zaak,
            betrokkene_type=RolTypes.niet_natuurlijk_persoon,
            betrokkene=BETROKKENE,
            rolomschrijving='Beslisser'
        )
        NietNatuurlijkPersoon.objects.create(
            rol=rol,
            ann_identificatie='123456',
        )
        zaak_url = get_operation_url('zaak_read', uuid=zaak.uuid)
        url = get_operation_url('rol_read', uuid=rol.uuid)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(
            data,
            {
                'url': f'http://testserver{url}',
                'zaak': f'http://testserver{zaak_url}',
                'betrokkene': BETROKKENE,
                'betrokkeneType': RolTypes.niet_natuurlijk_persoon,
                'rolomschrijving': 'Beslisser',
                'roltoelichting': '',
                'registratiedatum': '2018-01-01T00:00:00Z',
                'betrokkeneIdentificatie': {
                    'innNnpId': '',
                    'annIdentificatie': '123456',
                    'statutaireNaam': '',
                    'innRechtsvorm': '',
                    'bezoekadres': '',
                    'subVerblijfBuitenland': ''
                }
            }
        )

    def test_create_rol_with_identificatie(self):
        url = get_operation_url('rol_create')
        zaak = ZaakFactory.create()
        zaak_url = get_operation_url('zaak_read', uuid=zaak.uuid)
        data = {
            'zaak': f'http://testserver{zaak_url}',
            'betrokkene_type': RolTypes.natuurlijk_persoon,
            'rolomschrijving': 'Initiator',
            'roltoelichting': 'awerw',
            'betrokkeneIdentificatie': {
                'anpIdentificatie': '12345',
                }
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Rol.objects.count(), 1)
        self.assertEqual(NatuurlijkPersoon.objects.count(), 1)
        self.assertEqual(NietNatuurlijkPersoon.objects.count(), 0)

        rol = Rol.objects.get()
        natuurlijk_persoon = NatuurlijkPersoon.objects.get()

        self.assertEqual(rol.natuurlijkpersoon, natuurlijk_persoon)
        self.assertEqual(natuurlijk_persoon.anp_identificatie, '12345')

    def test_create_rol_without_identificatie(self):
        url = get_operation_url('rol_create')
        zaak = ZaakFactory.create()
        zaak_url = get_operation_url('zaak_read', uuid=zaak.uuid)
        data = {
            'zaak': f'http://testserver{zaak_url}',
            'betrokkene': BETROKKENE,
            'betrokkene_type': RolTypes.natuurlijk_persoon,
            'rolomschrijving': 'Initiator',
            'roltoelichting': 'awerw',
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Rol.objects.count(), 1)
        self.assertEqual(NatuurlijkPersoon.objects.count(), 0)

        rol = Rol.objects.get()

        self.assertEqual(rol.betrokkene, BETROKKENE)

    def test_create_rol_fail_validation(self):
        url = get_operation_url('rol_create')
        zaak = ZaakFactory.create()
        zaak_url = get_operation_url('zaak_read', uuid=zaak.uuid)
        data = {
            'zaak': f'http://testserver{zaak_url}',
            'betrokkene_type': RolTypes.natuurlijk_persoon,
            'rolomschrijving': 'Initiator',
            'roltoelichting': 'awerw',
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        validation_error = get_validation_errors(response, 'nonFieldErrors')

        self.assertEqual(validation_error['code'], 'invalid-betrokkene')

    @freeze_time("2018-01-01")
    def test_filter_rol_np_bsn(self):
        zaak = ZaakFactory.create()
        rol = RolFactory.create(
            zaak=zaak,
            betrokkene_type=RolTypes.natuurlijk_persoon,
            betrokkene='',
            rolomschrijving='Beslisser'
        )
        NatuurlijkPersoon.objects.create(
            rol=rol,
            inp_bsn='183068142',
            inp_a_nummer='1234567890'
        )

        rol_2 = RolFactory.create(
            zaak=zaak,
            betrokkene_type=RolTypes.natuurlijk_persoon,
            betrokkene='',
            rolomschrijving='Beslisser'
        )
        NatuurlijkPersoon.objects.create(
            rol=rol_2,
            inp_bsn='650237481',
            inp_a_nummer='2234567890'
        )

        rol_3 = RolFactory.create(
            zaak=zaak,
            betrokkene_type=RolTypes.vestiging,
            betrokkene='',
            rolomschrijving='Beslisser'
        )
        Vestiging.objects.create(
            rol=rol_3,
            vestigings_nummer='183068142'
        )

        url = get_operation_url('rol_list', uuid=rol.uuid)

        response = self.client.get(url, {'betrokkeneIdentificatie__natuurlijkPersoon__inpBsn': '183068142'})

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        data = response.json()

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['betrokkeneIdentificatie']['inpBsn'], '183068142')