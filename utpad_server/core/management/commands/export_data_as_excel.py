from django.core.management import BaseCommand
from django.db import IntegrityError

from utpad_server.dataload import save_data_to_excel


class Command(BaseCommand):
    help = 'Export all data as an Excel file'

    def add_arguments(self, parser):
        parser.add_argument('output_file', type=str, help='The output Excel file path')

    def handle(self, *args, **options):
        output_file = options['output_file']
        try:
            save_data_to_excel(output_file)
            self.stdout.write(self.style.SUCCESS(f'Successfully exported data to {output_file}'))
        except IntegrityError as e:
            self.stderr.write(self.style.ERROR(f'IntegrityError: {str(e)}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {str(e)}'))
