# pgadmin/Dockerfile

# Use the official pgAdmin image as a base
FROM dpage/pgadmin4

# Switch to root to perform operations
USER root

# Copy the server.json file into the container
COPY ../storage/server.json /pgadmin4/servers.json

# Copy the secrets file
COPY ../storage/secrets/secrets_database.env /pgpass

# Set the correct permissions for the pgpass file
RUN chmod 600 /pgpass

# Switch back to the pgadmin user
USER pgadmin

# The entrypoint is already set in the base image, so we don't need to specify it here