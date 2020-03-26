# fdbk

[![Build Status](https://travis-ci.org/kangasta/fdbk.svg?branch=master)](https://travis-ci.org/kangasta/fdbk)

Backend and DB wrapper for feedback collection system.

## Installation

Run:

```bash
pip install fdbk
```

to install from [PyPI](https://pypi.org/project/fdbk/) or download this repository and run

```bash
python setup.py install
```

to install from sources.

## Usage

### Running the server

Launch development server to port 8080 with:

```bash
fdbk-server -p 8080
```

See `fdbk-server --help` for other options. The server is configured via a configuration file: see example in examples directory.

## Testing

Check and automatically fix formatting with:

```bash
pycodestyle fdbk
autopep8 -aaar --in-place fdbk
```

Run static analysis with:

```bash
pylint -E --enable=invalid-name,unused-import,useless-object-inheritance fdbk
```

Run unit tests with command:

```bash
python3 -m unittest discover -s tst/
```

Get test coverage with commands:

```bash
coverage run --branch --source fdbk/ -m unittest discover -s tst/
coverage report -m
```
