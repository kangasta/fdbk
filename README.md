# fdbk

[![Build Status](https://travis-ci.org/kangasta/fdbk.svg?branch=master)](https://travis-ci.org/kangasta/fdbk)

Backend and DB wrapper for feedback collection system.

## Installation

Run:

```bash
pip install fdbk
```

## Usage

### Running the server

Launch development server to port 8080 with:

```bash
fdbk-server -p 8080
```

See `fdbk-server --help` for other options. The server is configured via a configuration file: see example in examples directory.

## Testing

Run unit tests with command:

```bash
python3 -m unittest discover -s fdbk/tst/
```

Get test coverage with commands:
```bash
coverage run -m unittest discover -s fdbk/tst/
coverage report -m
```
