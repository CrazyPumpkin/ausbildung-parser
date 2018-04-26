from datetime import date
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status

from apps.site_parser.models import Vacancy, City, Company
from apps.site_parser.serializers import VacancySerializer


class VacancyTests(TestCase):
    """
    Vacancy model tests
    """

    def setUp(self):
        company = Company(name='NORDSEE GmbH',
                          logo='https://www.ausbildung.de/uploads/image/2e/2e1728ba-85b0-1427-3664-828c3e20ecf7/corporation_logo_LOW_Wir_sind_Fisch_Final.jpg')
        city = City(name='Wien')

        self.vacancy = Vacancy(is_active=True,
                               title='Fachmann für Systemgastronomie (m/w)',
                               location=city, starts_at=date(2018, 1, 30),
                               description='', image_list='', company=company)

    def test_str(self):
        """
        Test 'str' method
        :return:
        """
        self.assertEquals(str(self.vacancy),
                          'Fachmann für Systemgastronomie (m/w) starts at 2018-01-30 | NORDSEE GmbH')


class CityTests(TestCase):
    """
    City model tests
    """

    def setUp(self):
        self.city = City(name='Salzburg')

    def test_str(self):
        """
        Test 'str' method
        :return:
        """
        self.assertEquals(str(self.city), 'Salzburg')


class CompanyTests(TestCase):
    """
    Company model tests
    """

    def setUp(self):
        self.company = Company(name='NORDSEE GmbH',
                               logo='https://www.ausbildung.de/uploads/image/2e/2e1728ba-85b0-1427-3664-828c3e20ecf7/corporation_logo_LOW_Wir_sind_Fisch_Final.jpg')

    def test_str(self):
        """
        Test 'str' method
        :return:
        """
        self.assertEquals(str(self.company), 'NORDSEE GmbH')


class VacanciesAPITest(APITestCase):
    """
    API tests
    """

    def setUp(self):
        self.company = Company.objects.create(name='NORDSEE GmbH',
                                              logo='https://www.ausbildung.de/uploads/image/2e/2e1728ba-85b0-1427-3664-828c3e20ecf7/corporation_logo_LOW_Wir_sind_Fisch_Final.jpg')
        self.city = City.objects.create(name='Wien')
        self.vacancy = Vacancy.objects.create(
            uuid='15b92c189c014b378040a7f0b7b09877', is_active=True,
            title='Fachmann für Systemgastronomie (m/w)',
            location=self.city, starts_at=date(2018, 1, 30),
            description='', image_list='', company=self.company)

    def test_vacancies_list(self):
        url = reverse('vacancies-list')
        response = self.client.get(url, format='json')
        vacancies = Vacancy.objects.all()
        serializer = VacancySerializer(vacancies, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
