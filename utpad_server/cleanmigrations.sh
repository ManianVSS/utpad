#!/bin/bash

timestamp=$(date +%F-%H:%M)
mkdir -p data/dbbackup/$timestamp/migrations

mv core/migrations data/dbbackup/$timestamp/migrations/core
mv capacity/migrations data/dbbackup/$timestamp/migrations/capacity
mv execution/migrations data/dbbackup/$timestamp/migrations/execution
