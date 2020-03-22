# Examples

## Example for Reporter usage

The `net_status/net_status.py` and `sys_status/sys_status.py` provide examples on how to use `fdbk.Reporter` to automatically push data from data source to fdbk. For example, run

```bash
python3 net_status/net_status.py -i 10 -n 5 -t Google https://google.com http://localhost:8080
```

to poll elapsed time of get request to Google with 5 sample averaging over 10 seconds or

```bash
python3 sys_status/sys_status.py -i 10 -n 5 http://localhost:8080
```

to poll system resource usage with same averaging. Both example commands push the data to fdbk server in port 8080 of localhost via fdbk ClientConnection.

## Example data for POST requests

The `post_data/data-*.json` and `post_data/topic.json` are example data for `/topic/<topic>/data` and `/topic` POST requests, respectively. Example usage:

```bash
response=$(curl -sd @post_data/topic.json -H "Content-Type: application/json" -X POST -L localhost:8080/topics);

# Get value of topic_id field from response JSON
topic_id=$(echo "${response}" | python3 -c "import json,sys; print(json.load(sys.stdin)['topic_id']);");

for i in 1 2 3 4 5; do
    curl -d @post_data/data-${i}.json -H "Content-Type: application/json" -X POST -L localhost:8080/topics/${topic_id}/data;
done;
```

## Example config data

The `config.json` file is a example config file that can be passed on to `fdbk-server`. Example usage:

```bash
fdbk-server --config-file config.json
```
