import os
import sys
import logging
import time

from datetime import datetime
from urllib import parse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from apps.site_parser.models import City, Company, Vacancy

"""Settings for local testing on Linux/Mac with Chrome driver"""

LINUX_PLATFORM = 'linux'
MAC_PLATFORM = 'darwin'

WEB_DRIVERS = {
    LINUX_PLATFORM: 'chromedriver_linux_x64',
    MAC_PLATFORM: 'chromedriver_darwin'
}

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
try:
    DRIVER_PATH = os.path.join(CURRENT_PATH, 'drivers',
                               WEB_DRIVERS[sys.platform])
except:
    raise Exception

logger = logging.getLogger('parser')


class BaseParser():
    """
    Base class for import data from ausbildung.de
    """

    # Pages to scrap
    URLS = {
        'filter_page': 'https://www.ausbildung.de/suche/',
    }

    def __init__(self, *args, **kwargs):
        """
        Init base parser
        """
        self.browser = self._setup_browser()

    @staticmethod
    def _setup_browser():
        """
        Prepare webdriver
        :return: 
        """
        logger.info("setup browser")
        chrome_bin = os.environ.get('GOOGLE_CHROME_SHIM', None)

        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.binary_location = chrome_bin

        return webdriver.Chrome(chrome_options=options)


class Parser(BaseParser):
    """
    Main parser
    """

    def __init__(self, *args, **kwargs):
        """
        Init parser
        """
        logger.info("init parser")
        super(Parser, self).__init__(*args, **kwargs)
        self.filter_form = None
        self.vacancy_links = []

    def run(self):
        """
        Run parsing
        """
        logger.info("run parser")
        self.browser.get(self.URLS['filter_page'])
        self._prepare_filters()
        self._handle_results()
        self._parse_vacancy_page()
        logger.info("successfully parsed")

    def _prepare_filters(self):
        """
        Fill filters
        """
        logger.info("fill filters")

        form_id = 'new_form_main_search'
        logger.info("try to get form with filters")
        self.filter_form = WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.ID, form_id)))

        self._fill_query()
        self._fill_filters()
        self._submit_filters()

    def _fill_query(self):
        """
        Paste query word into field
        """
        logger.info("fill query")
        search_input_id = 'main-search-what'
        query = 'nordsee'
        # fill search query
        self.filter_form.find_element_by_id(search_input_id).send_keys(query)

    def _fill_filters(self):
        """
        Fill filters inputs
        """
        logger.info("fill filters inputs")

        searched_industry = 'Gastronomie / Tourismus'
        filter_box_class = 'filter-box'
        range_id = 'form_main_search_radius'
        industry_select_id = 'form_main_search_industry_public_id'

        logger.info("try to open block with filters")
        # click to open filters
        filter_box = self.filter_form.find_element_by_class_name(
            filter_box_class)
        filter_box.click()

        logger.info("try to set range")
        # set range to 100 km
        range_filter = filter_box.find_element_by_id(range_id)
        self.browser.execute_script(
            "arguments[0].setAttribute('value', 100)", range_filter)

        logger.info("try to select searched industry")
        # industry select
        industry_select = filter_box.find_element_by_id(industry_select_id)
        subelement_class = 'selectize-control'
        parent = industry_select.find_element_by_xpath('..')
        subelement = parent.find_element_by_class_name(subelement_class)
        subelement.click()

        option = subelement.find_element_by_xpath(
            "//div[@class='option'][contains(text(), '{}')]".format(
                searched_industry))
        option.click()

    def _submit_filters(self):
        """
        Submit filters form
        """
        logger.info("submit form with filters")
        self.filter_form.submit()

    def _handle_results(self):
        """
        Parse filtered results
        """
        logger.info("handle results")
        results_wrapper_class = 'search-result__wrapper'
        card_class = 'simple-card'

        WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, card_class)))

        results_count = self._get_results_count()
        current_count = len(
            self.browser.find_elements_by_class_name(card_class))

        logger.info("scroll to view all results")
        while current_count < results_count:
            self._next_page()
            current_count = len(
                self.browser.find_elements_by_class_name(card_class))

        logger.info("get wrapper with results")
        results = self.browser.find_element_by_class_name(
            results_wrapper_class)

        cards = results.find_elements_by_class_name(card_class)

        actual_vacancies_ids = []

        logger.info("handle cards")
        for card in cards:
            actual_vacancies_ids.append(self._handle_card(card))

        logger.info("handling cards ends, set old vacancies inactive")

        # set old vacancies inactive
        Vacancy.objects.exclude(id__in=actual_vacancies_ids).update(
            is_active=False)

    def _handle_card(self, card):
        """
        Parse card info
        :param card: handling card
        :return:
        """
        logger.info("handle card")
        vacancy_title = card.find_element_by_tag_name("h3").text
        company_name = card.find_element_by_tag_name(
            "h4").find_element_by_tag_name(
            "strong").text
        start_date_str = card.find_element_by_class_name(
            'fact__content--calendar').find_element_by_class_name('value').text

        try:
            vacancy_start_date = datetime.strptime(start_date_str, '%d.%m.%Y')
        except:
            vacancy_start_date = None

        city_name = card.find_element_by_class_name(
            'fact__content--location').find_element_by_class_name('value').text

        company_logo = card.find_element_by_class_name(
            'simple-card__logo-overlay').get_attribute('src')

        vacancy_link = card.find_element_by_class_name(
            'simple-card__link').get_attribute('href')
        self.vacancy_links.append(vacancy_link)
        vacancy_uuid = \
        parse.parse_qs(parse.urlparse(vacancy_link).query)['vacancy'][0]

        logger.info(
            "{} {} {} {}".format(vacancy_title, company_name, start_date_str,
                                 city_name, company_logo))

        logger.info("save parsed data to database")
        city, _ = City.objects.get_or_create(name=city_name)
        company, _ = Company.objects.update_or_create(name=company_name,
                                                      defaults={
                                                          'logo': company_logo})
        # vacancy data to update
        vacancy_data = {
            'title': vacancy_title,
            'starts_at': vacancy_start_date,
            'location': city,
            'company': company,
            'is_active': True
        }
        # update or create vacancies
        vacancy, _ = Vacancy.objects.update_or_create(uuid=vacancy_uuid,
                                                      defaults=vacancy_data)
        logger.info("data saved successfully")
        return vacancy.id

    def _get_results_count(self):
        """
        Get results count
        """
        return int(self.browser.find_element_by_class_name('blob').text)

    def _next_page(self):
        """
        Scroll page to next one
        """
        try:
            self.browser.find_element_by_class_name(
                'js-load-more-button-here').click()
        except:
            self.browser.execute_script(
                'window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(2)

    def _parse_vacancy_page(self):
        logger.info("parse vacancy pages")
        for link in self.vacancy_links:
            self.browser.get(link)

            # update description value of vacancy
            vacancy_uuid = \
                parse.parse_qs(parse.urlparse(link).query)['vacancy'][0]
            vacancy_descr = self.browser.find_element_by_class_name(
                'entity-description__description').text

            # update image list value of vacancy
            vacancy_images_block = self.browser.find_element_by_class_name(
                'quadruple-media__media-list')
            vacancy_images_list = vacancy_images_block.find_elements_by_tag_name(
                'img')
            image_list = []
            for image in vacancy_images_list:
                image_list.append(image.get_attribute('src'))

            Vacancy.objects.filter(uuid=vacancy_uuid).update(
                description=vacancy_descr, image_list=image_list)
            logger.info(
                "successfully updated vacancy uuid-{}".format(vacancy_uuid))
