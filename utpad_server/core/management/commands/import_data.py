from django.core.management import BaseCommand
from django.db import IntegrityError

from utpad_server.dataload import load_data_from_folder


class Command(BaseCommand):
    help = 'Import data from YAML files to database'

    def add_arguments(self, parser):
        parser.add_argument('data_folder', type=str, help='The folder where data files are located')

    def handle(self, *args, **options):
        data_folder = options['data_folder']
        try:
            load_data_from_folder(data_folder)
            self.stdout.write(self.style.SUCCESS(f'Successfully imported data from {data_folder}'))
        except IntegrityError as e:
            self.stderr.write(self.style.ERROR(f'Error importing data: {e}'))
