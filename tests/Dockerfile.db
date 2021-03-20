FROM "library/postgres:13"
# As of 2021/03/20, apt's postgresql-plpython3-13 is version 3.7.3
RUN apt-get update && apt-get install --yes postgresql-plpython3-13
COPY ./_init.sql /docker-entrypoint-initdb.d/
