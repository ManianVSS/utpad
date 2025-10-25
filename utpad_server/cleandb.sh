#!/bin/bash

bash cleanmigrations.sh

mv data/db.sqlite3 data/dbbackup/$timestamp

bash migrate.sh

python manage.py create_super_user
python manage.py create_default_configuration