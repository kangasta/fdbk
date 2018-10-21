# Examples

## Example data for POST requests

The `data-*.json` and `topic.json` are example data for `/add/data/<topic>` and `/add/topic` POST requests, respectively. Example usage:

```bash
curl -d @topic.json -H "Content-Type: application/json" -X POST -L localhost:8080/add/topic?token=2f45;

for i in 1 2 3 4 5; do
	curl -d @data-${i}.json -H "Content-Type: application/json" -X POST -L localhost:8080/add/data/APA?token=2f45;
done;
```

## Example config data

The `config.json` file is a example config file that can be passed on to `fdbk-server`. Example usage:

```bash
fdbk-server --config-file config.json
```
