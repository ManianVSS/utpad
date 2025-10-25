@echo off

call cleanmigrations.bat

move data\db.sqlite3 data\dbbackup\%fullstamp%\migrations

call migrate.bat

python manage.py create_super_user
python manage.py create_default_configuration