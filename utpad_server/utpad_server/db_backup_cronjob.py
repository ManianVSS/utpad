from django.core import management


def backup():
    management.call_command('dbbackup')
    management.call_command('mediabackup')
