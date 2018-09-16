# revolut-python

[![Travis](https://img.shields.io/travis/tducret/revolut-python.svg)](https://travis-ci.org/tducret/revolut-python)
[![Coveralls github](https://img.shields.io/coveralls/github/tducret/revolut-python.svg)](https://coveralls.io/github/tducret/revolut-python)
[![PyPI](https://img.shields.io/pypi/v/revolut.svg)](https://pypi.org/project/revolut/)
![License](https://img.shields.io/github/license/tducret/revolut-python.svg)

# Description

Non-official client for the [Revolut Bank](https://www.revolut.com/)

I wrote a French blog post about it [here](https://www.tducret.com/scraping/2018/08/17/un-robot-d-achat-et-de-vente-de-bitcoins-developpe-en-python.html)

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
  -a, --account TEXT   account name (ex : "EUR CURRENT") to get the balance
                       for the account
  --version            Show the version and exit.
  --help               Show this message and exit.
 ```

 Example output :

 ```csv
Account name,Balance,Currency
EUR CURRENT,100.50,EUR
GBP CURRENT,20.00,GBP
USD CURRENT,0.00,USD
AUD CURRENT,0.00,AUD
BTC CURRENT,0.00123456,BTC
EUR SAVINGS (My vault),10.30,EUR
```

If you don't have a Revolut token yet, the tool will allow you to obtain one.

## TODO

- [ ] Document revolutbot.py
- [ ] Create a RaspberryPi Dockerfile for revolutbot (to check if rates grows very often)
- [ ] Improve coverage for revolutbot
