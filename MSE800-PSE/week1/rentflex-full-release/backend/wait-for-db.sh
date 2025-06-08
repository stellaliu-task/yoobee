#!/bin/sh
# wait-for-db.sh

set -e

host="$DB_HOST"
port="$DB_PORT"

echo "Waiting for MySQL database... ($host:$port)"
until nc -z $host $port; do
  echo "MySQL is not ready yet - waiting..."
  sleep 2
done

echo "MySQL database port is accessible!"
echo "Executing command: $@"
exec "$@" 