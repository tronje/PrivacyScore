#!/bin/bash

# required services
echo "Starting services..."

for service in "postgresql" "redis" "rabbitmq"; do
    sudo systemctl is-active $service.service
    if [ $? -ne 0 ]; then
        sudo systemctl start $service.service
    fi
done

echo "done"
echo ""

# celery workers
echo "Starting celery workers..."
venv/bin/celery -A privacyscore worker -E -Q master -n master_worker &
venv/bin/celery -A privacyscore worker -E -Q slave &
echo "done"
echo ""

# start django app
venv/bin/python manage.py runserver
