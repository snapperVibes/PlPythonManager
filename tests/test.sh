#! /usr/bin/env bash
trap "docker-compose -f tests/docker-compose.yml down -v --remove-orphans" EXIT

# Exit in case of error
set -e

docker-compose -f tests/docker-compose.yml down -v --remove-orphans # Remove possibly previous broken stacks left hanging after an error

if [ $(uname -s) = "Linux" ]; then
    echo "Remove __pycache__ files"
    sudo find . -type d -name __pycache__ -exec rm -r {} \+
fi

docker-compose -f tests/docker-compose.yml build
docker-compose -f tests/docker-compose.yml up -d
#sleep 3
docker-compose -f tests/docker-compose.yml exec -T tester pytest /src/tests/
