# Examples

The `net_status/net_status.py` and `sys_status/sys_status.py` provide examples on how to use `fdbk.Reporter` to automatically push data from data source to fdbk. For example, run

```bash
python3 net_status/net_status.py -i 10 -n 5 -t Google https://google.com http://localhost:8080
```

to poll elapsed time of get request to Google with 5 sample averaging over 10 seconds or

```bash
python3 sys_status/sys_status.py -i 10 -n 5 http://localhost:8080
```

to poll system resource usage with same averaging. Both example commands push the data to fdbk server in port 8080 of localhost via fdbk ClientConnection.
