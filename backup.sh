HETZNER_VOLUME_NAME=HC_Volume_101326655
DOCKER_VOLUME_NAME=s_locator_db_data
OUTPUT_FILE_PATH="/backup.log"


## Check if output file exists
if [ ! -f $OUTPUT_FILE_PATH ]; then
        touch $OUTPUT_FILE_PATH
fi

rsync -r --delete /var/lib/docker/volumes/$DOCKER_VOLUME_NAME/ /mnt/$HETZNER_VOLUME_NAME/$DOCKER_VOLUME_NAME/

echo "On : $(date) , BACKUP Dest: /mnt/$HETZNER_VOLUME_NAME/$DOCKER_VOLUME_NAME , Src : /var/lib/docker/volumes/$DOCKER_VOLUME_NAME" >> $OUTPUT_FILE_PATH