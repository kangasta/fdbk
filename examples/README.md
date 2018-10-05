# Examples

## Example data for POST requests

The `data.json` and `topic.json` are example data for `/add/data/<topic>` and `/add/topic` POST requests, respectively. Example usage:

```bash
curl -d @topic.json -H "Content-Type: application/json" -X POST -L localhost:3030/add/topic?token=2f45;

curl -d @data.json -H "Content-Type: application/json" -X POST -L localhost:3030/add/data/APA?token=2f45;
```

## Example config data

The `config.json` file is a example config file that can be passed on to `fdbk-server`. Example usage:

```bash
fdbk-server --config-file config.json
```
