from django.core.management import BaseCommand

from core.models import Configuration


class Command(BaseCommand):
    help = 'Creates default configuration values in Configuration table'

    def handle(self, *args, **options):
        try:
            database_name_config = Configuration.objects.filter(name="site_name")
            if database_name_config.count() == 0:
                Configuration(name='site_name', value='Utpad Team Management',
                              description='The name of the site.').save()
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error creating default configuration: {str(e)}'))
