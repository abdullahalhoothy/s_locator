FROM postgres:13

# Copy initialization scripts
COPY init.sql /docker-entrypoint-initdb.d/

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN ["chmod","777","/usr/local/bin/docker-entrypoint.sh"]

# You can add more customizations here if needed
# For example, you could install extensions or set configuration options