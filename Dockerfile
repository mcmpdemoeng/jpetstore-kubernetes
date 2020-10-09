FROM mysql:5.5
ADD jpetstore/db/mysql5/*.sql /docker-entrypoint-initdb.d/
COPY jpetstore/db/mysql5/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh