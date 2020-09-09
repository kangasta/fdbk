# Examples

This directory contains usage examples of `fdbk` as well as its plugins and UI.

## Reporter

The `net_status/net_status.py` and `sys_status/sys_status.py` provide examples on how to use `fdbk.Reporter` to automatically push data from data source to fdbk. For example, run

```bash
python3 net_status/net_status.py -i 10 -n 5 -t Google https://google.com http://localhost:8080
```

to poll elapsed time of get request to Google with 5 sample averaging over 10 seconds or

```bash
python3 sys_status/sys_status.py -i 10 -n 5 http://localhost:8080
```

to poll system resource usage with same averaging. Both example commands push the data to fdbk server in port 8080 of localhost via fdbk ClientConnection.

## Docker Compose setup

The `net_status/` directory also includes an example docker-compose setup for plugin usage and displaying the data on an UI. To launch this example, ensure that you have Docker and docker-compose installed and run:

```bash
cd net_status/
docker-compose up --build
```
