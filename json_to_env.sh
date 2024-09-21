JSON_FILE="123secrets_variables.json"
ENV_FILE=".env"

jq -r 'to_entries | .[] | "\(.key)=\(.value)"' "$JSON_FILE" > "$ENV_FILE"
