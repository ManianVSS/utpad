#!/bin/bash

python3 manage.py makemigrations core
python3 manage.py makemigrations capacity
python3 manage.py makemigrations execution

python3 manage.py migrate
