# Examples

## Example data for POST requests

The `data-*.json` and `topic.json` are example data for `/add/data/<topic>` and `/add/topic` POST requests, respectively. Example usage:

```bash
response=$(curl -sd @topic.json -H "Content-Type: application/json" -X POST -L localhost:8080/add/topic);

# Get value of topic_id field from response JSON
topic_id=$(echo "$response" | python3 -c "import json,sys; print(json.load(sys.stdin)['topic_id']);");

for i in 1 2 3 4 5; do
	curl -d @data-${i}.json -H "Content-Type: application/json" -X POST -L localhost:8080/add/data/$topic_id;
done;
```

## Example config data

The `config.json` file is a example config file that can be passed on to `fdbk-server`. Example usage:

```bash
fdbk-server --config-file config.json
```
