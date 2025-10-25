from django.core.management import BaseCommand
from django.db import IntegrityError

from utpad_server.dataload import save_data_to_folder


class Command(BaseCommand):
    help = 'Export data from database to YAML files'

    def add_arguments(self, parser):
        parser.add_argument('data_folder', type=str, help='The folder where data will be exported')

    def handle(self, *args, **options):
        data_folder = options['data_folder']
        try:
            save_data_to_folder(data_folder)
            self.stdout.write(self.style.SUCCESS(f'Successfully exported data to {data_folder}'))
        except IntegrityError as e:
            self.stderr.write(self.style.ERROR(f'Error exporting data: {e}'))
