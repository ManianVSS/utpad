from django.contrib.auth.models import User
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Create super user with default credentials if not exists'

    def add_arguments(self, parser):
        """
        Add command line arguments
        Optional command line arguments are username and password defaulting to 'admin' and 'password' respectively
        :param parser:
        :return:
        """
        parser.add_argument('username', type=str, nargs='?', default='admin', help='Username for the super user')
        parser.add_argument('password', type=str, nargs='?', default='password', help='Password for the super user')
        parser.add_argument('email', type=str, nargs='?', default='admin@example.com', help='Email for the super user')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']

        try:
            try:
                User.objects.get(username=username)
                self.stdout.write(self.style.WARNING(f'Supper user "{username}" already exists'))
            except User.DoesNotExist:
                created_user = User.objects.create_superuser(username, email, password)
                self.stdout.write(self.style.SUCCESS(f'Successfully created super user "{username}"'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error creating super user: {str(e)}'))
