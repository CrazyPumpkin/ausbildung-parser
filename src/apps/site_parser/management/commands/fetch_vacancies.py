import time
from django.core.management.base import BaseCommand

from apps.site_parser.utils import Parser


class Command(BaseCommand):
    help = 'Fetch vacancies from www.ausbildung.de'

    def handle(self, *args, **options):
        parser = Parser()
        parser.run()
