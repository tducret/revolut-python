# -*- coding: utf-8 -*-
""" This package allows you to communicate with yout Revolut accounts
"""

import requests
import json
from urllib.parse import urljoin
import os

_DEVICE_ID = os.environ.get('REVOLUT_DEVICE_ID', None)
_TOKEN = os.environ.get('REVOLUT_TOKEN', None)

if _TOKEN is None:
    raise OSError('REVOLUT_TOKEN environment variable not set')
elif _DEVICE_ID is None:
    raise OSError('REVOLUT_DEVICE_ID environment variable not set')

_URL_GET_ACCOUNTS = "https://api.revolut.com/user/current/wallet"
_URL_QUOTE = "https://api.revolut.com/quote/"

_AVAILABLE_CURRENCIES = ["USD", "RON", "HUF", "CZK", "GBP", "CAD", "THB",
                         "SGD", "CHF", "AUD", "ILS", "DKK", "PLN", "MAD",
                         "AED", "EUR", "JPY", "ZAR", "NZD", "HKD", "TRY",
                         "QAR", "NOK", "SEK", "BTC"]

# The amounts are stored as integer on Revolut.
# They apply a scale factor depending on the currency
_DEFAULT_SCALE_FACTOR = 100
_SCALE_FACTOR_CURRENCY_DICT = {
                                "EUR": 100,
                                "BTC": 100000000,
                               }


class Amount(object):
    """ Class to handle the Revolut amount with currencies """
    def __init__(self, currency, revolut_amount=None, real_amount=None):
        if currency not in _AVAILABLE_CURRENCIES:
            raise KeyError(currency)
        self.currency = currency

        if revolut_amount is not None:
            if type(revolut_amount) not in [int]:
                raise TypeError(type(revolut_amount))
            self.revolut_amount = revolut_amount
            self.real_amount = self.get_real_amount()
        elif real_amount is not None:
            if type(real_amount) not in [int, float]:
                raise TypeError(type(real_amount))
            self.real_amount = real_amount
            self.revolut_amount = self.get_revolut_amount()
        else:
            raise ValueError("revolut_amount or real_amount must be set")

    def __str__(self):
        if self.currency == "BTC":
            digits_after_float = 8
        else:
            digits_after_float = 2

        return("%.*f %s" % (digits_after_float,
                            self.real_amount,
                            self.currency))

    def get_real_amount(self):
        """ Get the real amount from a Revolut amount
        >>> a = Amount(revolut_amount=100, currency="EUR")
        >>> a.get_real_amount()
        1.0
        """
        scale = _SCALE_FACTOR_CURRENCY_DICT.get(
                self.currency, _DEFAULT_SCALE_FACTOR)
        return (self.revolut_amount/scale)

    def get_revolut_amount(self):
        """ Get the Revolut amount from a real amount
        >>> a = Amount(real_amount=1, currency="EUR")
        >>> a.get_revolut_amount()
        100
        """
        scale = _SCALE_FACTOR_CURRENCY_DICT.get(
                self.currency, _DEFAULT_SCALE_FACTOR)
        return (self.real_amount*scale)


class Client(object):
    """ Do the requests with the Revolut servers """
    def __init__(self):
        self.session = requests.session()
        self.headers = {
                    'Host': 'api.revolut.com',
                    'X-Api-Version': '1',
                    'X-Device-Id': _DEVICE_ID,
                    'Authorization': _TOKEN,
                    }

    def _get(self, url):
        ret = self.session.get(url, headers=self.headers)
        if (ret.status_code != 200):
            raise ConnectionError
        return ret


def get_accounts():
    """ Get the account balance for each currency """
    c = Client()
    ret = c._get(_URL_GET_ACCOUNTS)
    raw_accounts = json.loads(ret.text)

    accounts = []
    for raw_account in raw_accounts.get("pockets"):
        account = {}
        account["balance"] = raw_account.get("balance")
        account["currency"] = raw_account.get("currency")
        accounts.append(account)
    return accounts


def get_last_transaction_from_csv(filename="exchange_history.csv"):
    return {
                'date': '07/07/2018',
                'hour': '08:45:30',
                'from_amount': 0.00003555,
                'from_currency': 'BTC',
                'to_amount': 20.55,
                'to_currency': 'EUR',
            }


def quote(from_amount, to_currency):
    if type(from_amount) != Amount:
        raise TypeError

    url_quote = urljoin(_URL_QUOTE, ("%s%s?amount=%d&side=SELL" %
                                     (from_amount.currency,
                                      to_currency,
                                      from_amount.revolut_amount)))
    c = Client()
    ret = c._get(url_quote)
    raw_quote = json.loads(ret.text)
    quote_obj = Amount(revolut_amount=raw_quote["to"]["amount"],
                       currency=to_currency)
    return quote_obj


def exchange(from_amount, from_currency, to_currency):
    return float(from_amount*2)


def write_a_transaction_to_csv(filename):
    return True
