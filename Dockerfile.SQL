FROM postgres:10.21-alpine3.16
ADD database.sql /docker-entrypoint-initdb.d
ADD scripts_sql/import.sh  /docker-entrypoint-initdb.d
COPY database.sql .  