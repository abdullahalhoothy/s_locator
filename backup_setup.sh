## Setup for backup is needed for the first time only
HETZNER_VOLUME_NAME=HC_Volume_101326655
DOCKER_VOLUME_NAME=s_locator_db_data

if [ ! -d "/var/lib/docker/volumes/$DOCKER_VOLUME_NAME" ]; then
    if [ -d "/mnt/$HETZNER_VOLUME_NAME/$DOCKER_VOLUME_NAME/" ]; then
    mkdir -p /var/lib/docker/volumes/$DOCKER_VOLUME_NAME
    rsync -r --delete /mnt/$HETZNER_VOLUME_NAME/$DOCKER_VOLUME_NAME/ /var/lib/docker/volumes/$DOCKER_VOLUME_NAME/
    fi
fi


## Crontab config
CRON_JOB="/backup.sh"
output=$(crontab -l | grep -c "$CRON_JOB")
if [ ! $output -eq 0 ]; then
    echo "Cron job already exists."
else
    (crontab -l; echo "*/50 * * * * /backup.sh") | crontab -
    echo "Cron job added."
fi