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

⚠️ **If you don't receive a SMS when trying to get a token, you need to logout from the app on your Smartphone.**

## Pulling transactions

```bash
Usage: revolut_transactions.py [OPTIONS]

  Get the account balances on Revolut

Options:
  -t, --token TEXT            your Revolut token (or set the env var
                              REVOLUT_TOKEN)
  -l, --language TEXT         language ("fr" or "en"), for the csv header and
                              separator
  -t, --from_date [%Y-%m-%d]  transactions lookback date in YYYY-MM-DD format
                              (ex: "2019-10-26"). Default 30 days back
  -r, --reverse               reverse the order of the transactions displayed
  --help                      Show this message and exit.
```

 Example output :

 ```csv
Date-time,Description,Amount,Currency
08/26/2019 21:31:00,Card Delivery Fee,-59.99,SEK
09/14/2019 12:50:07,donkey.bike **pending**,0.0,SEK
09/14/2019 13:03:15,Top-Up by *6458,200.0,SEK
09/30/2019 16:19:19,Reward user for the invite,200.0,SEK
10/12/2019 23:51:02,Tiptapp Reservation,-250.0,SEK
```

## TODO

- [ ] Document revolutbot.py
- [ ] Create a RaspberryPi Dockerfile for revolutbot (to check if rates grows very often)
- [ ] Improve coverage for revolutbot
