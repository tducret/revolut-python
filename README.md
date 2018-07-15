# revolut-python

[![Travis](https://img.shields.io/travis/tducret/revolut-python.svg)](https://travis-ci.org/tducret/revolut-python)
[![Coveralls github](https://img.shields.io/coveralls/github/tducret/revolut-python.svg)](https://coveralls.io/github/tducret/revolut-python)
[![PyPI](https://img.shields.io/pypi/v/revolut.svg)](https://pypi.org/project/revolut/)
![License](https://img.shields.io/github/license/tducret/revolut-python.svg)

# Description

Non-official client for the [Revolut Bank](https://www.revolut.com/)

# Requirements

- Python 3
- pip3

# Installation

```bash
pip3 install -U revolut
```

## CLI tool : revolut_cli.py

```bash
Usage: revolut_cli.py [OPTIONS]

  Get the account balances on Revolut

Options:
  -t, --token TEXT     your Revolut token (or set the env var REVOLUT_TOKEN)
  -l, --language TEXT  language ("fr" or "en"), for the csv header and
                       separator
  --version            Show the version and exit.
  --help               Show this message and exit.
 ```

 Example output :

 ```csv
Account name,Balance,Currency
EUR wallet,100.50,EUR
GBP wallet,20.00,GBP
USD wallet,0.00,USD
AUD wallet,0.00,AUD
BTC wallet,0.00123456,BTC
```

If you don't have a Revolut token yet, the tool will allow you to obtain one.

## TODO

- [x] Create a CLI tool to get the balance (like https://github.com/tducret/ingdirect-python)
- [x] Explain how to use the CLI tool
- [x] Create a tool to exchange automatically a currency when it grows
- [x] Create the PIP package
- [x] Create the Docker image
- [x] Implement the function to get the last transactions
- [ ] Document revolutbot.py
- [ ] Add revolutbot to the revolut Pypi package
- [ ] Create a RaspberryPi Dockerfile for revolutbot (to check if rates grows very often)
- [ ] Improve coverage for revolutbot