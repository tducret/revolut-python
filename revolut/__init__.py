# -*- coding: utf-8 -*-
""" This package allows you to communicate with yout Revolut accounts
"""

import requests
import json
from urllib.parse import urljoin

__version__ = '0.0.3'  # Should be the same in setup.py

_URL_GET_ACCOUNTS = "https://api.revolut.com/user/current/wallet"
_URL_QUOTE = "https://api.revolut.com/quote/"
_URL_EXCHANGE = "https://api.revolut.com/exchange"

_AVAILABLE_CURRENCIES = ["USD", "RON", "HUF", "CZK", "GBP", "CAD", "THB",
                         "SGD", "CHF", "AUD", "ILS", "DKK", "PLN", "MAD",
                         "AED", "EUR", "JPY", "ZAR", "NZD", "HKD", "TRY",
                         "QAR", "NOK", "SEK", "BTC", "ETH", "XRP", "BCH",
                         "LTC"]

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
            if type(revolut_amount) != int:
                raise TypeError(type(revolut_amount))
            self.revolut_amount = revolut_amount
            self.real_amount = self.get_real_amount()
        elif real_amount is not None:
            if type(real_amount) not in [float, int]:
                raise TypeError(type(real_amount))
            self.real_amount = float(real_amount)
            self.revolut_amount = self.get_revolut_amount()
        else:
            raise ValueError("revolut_amount or real_amount must be set")

        self.real_amount_str = self.get_real_amount_str()

    def get_real_amount_str(self):
        """ Get the real amount with the proper format, without currency """
        if self.currency == "BTC":
            digits_after_float = 8
        else:
            digits_after_float = 2

        return("%.*f" % (digits_after_float, self.real_amount))

    def __str__(self):
        return('{} {}'.format(self.real_amount_str, self.currency))

    def get_real_amount(self):
        """ Get the real amount from a Revolut amount
        >>> a = Amount(revolut_amount=100, currency="EUR")
        >>> a.get_real_amount()
        1.0
        """
        scale = _SCALE_FACTOR_CURRENCY_DICT.get(
                self.currency, _DEFAULT_SCALE_FACTOR)
        return float(self.revolut_amount/scale)

    def get_revolut_amount(self):
        """ Get the Revolut amount from a real amount
        >>> a = Amount(real_amount=1, currency="EUR")
        >>> a.get_revolut_amount()
        100
        """
        scale = _SCALE_FACTOR_CURRENCY_DICT.get(
                self.currency, _DEFAULT_SCALE_FACTOR)
        return int(self.real_amount*scale)


class Client(object):
    """ Do the requests with the Revolut servers """
    def __init__(self, token, device_id):
        self.session = requests.session()
        self.headers = {
                    'Host': 'api.revolut.com',
                    'X-Api-Version': '1',
                    'X-Device-Id': device_id,
                    'Authorization': 'Basic '+token,
                    }

    def _get(self, url):
        ret = self.session.get(url=url, headers=self.headers)
        if (ret.status_code != 200):
            raise ConnectionError(
                'Status code {status} for url {url}\n{content}'.format(
                    status=ret.status_code, url=url, content=ret.text))
        return ret

    def _post(self, url, post_data):
        ret = self.session.post(url=url,
                                headers=self.headers,
                                data=post_data)
        if (ret.status_code != 200):
            raise ConnectionError(
                'Status code {status} for url {url}\n{content}'.format(
                    status=ret.status_code, url=url, content=ret.text))
        return ret


class Revolut(object):
    def __init__(self, token, device_id):
        self.client = Client(token=token, device_id=device_id)

    def get_account_balances(self):
        """ Get the account balance for each currency
        and returns it as a dict {"balance":XXXX, "currency":XXXX} """
        ret = self.client._get(_URL_GET_ACCOUNTS)
        raw_accounts = json.loads(ret.text)

        account_balances = []
        for raw_account in raw_accounts.get("pockets"):
            account_balance = {}
            account_balance["balance"] = raw_account.get("balance")
            account_balance["currency"] = raw_account.get("currency")
            account_balances.append(account_balance)
        self.account_balances = Accounts(account_balances)
        return self.account_balances

    def quote(self, from_amount, to_currency):
        if type(from_amount) != Amount:
            raise TypeError("from_amount must be with the Amount type")

        if to_currency not in _AVAILABLE_CURRENCIES:
                raise KeyError(to_currency)

        url_quote = urljoin(_URL_QUOTE, '{}{}?amount={}&side=SELL'.format(
            from_amount.currency,
            to_currency,
            from_amount.revolut_amount))
        ret = self.client._get(url_quote)
        raw_quote = json.loads(ret.text)
        quote_obj = Amount(revolut_amount=raw_quote["to"]["amount"],
                           currency=to_currency)
        return quote_obj

    def exchange(self, from_amount, to_currency, simulate=False):
        if type(from_amount) != Amount:
            raise TypeError("from_amount must be with the Amount type")

        if to_currency not in _AVAILABLE_CURRENCIES:
                raise KeyError(to_currency)

        data = '{"fromCcy":"%s","fromAmount":%d,"toCcy":"%s","toAmount":null}'\
            % (from_amount.currency,
               from_amount.revolut_amount,
               to_currency)

        if simulate:
            # Because we don't want to exchange currencies
            # for every test ;)
            simu = '[{"account":{"id":"FAKE_ID"},\
            "amount":-1,"balance":0,"completedDate":123456789,\
            "counterpart":{"account":\
            {"id":"FAKE_ID"},\
            "amount":170,"currency":"BTC"},"currency":"EUR",\
            "description":"Exchanged to BTC","direction":"sell",\
            "fee":0,"id":"FAKE_ID",\
            "legId":"FAKE_ID","rate":0.0001751234,\
            "startedDate":123456789,"state":"COMPLETED","type":"EXCHANGE",\
            "updatedDate":123456789},\
            {"account":{"id":"FAKE_ID"},"amount":170,\
            "balance":12345,"completedDate":12345678,"counterpart":\
            {"account":{"id":"FAKE_ID"},\
            "amount":-1,"currency":"EUR"},"currency":"BTC",\
            "description":"Exchanged from EUR","direction":"buy","fee":0,\
            "id":"FAKE_ID",\
            "legId":"FAKE_ID",\
            "rate":5700.0012345,"startedDate":123456789,\
            "state":"COMPLETED","type":"EXCHANGE",\
            "updatedDate":123456789}]'
            raw_exchange = json.loads(simu)
        else:
            ret = self.client._post(url=_URL_EXCHANGE, post_data=data)
            raw_exchange = json.loads(ret.text)

        if raw_exchange[0]["state"] == "COMPLETED":
            amount = raw_exchange[0]["counterpart"]["amount"]
            currency = raw_exchange[0]["counterpart"]["currency"]
            exchanged_amount = Amount(revolut_amount=amount,
                                      currency=currency)
        else:
            raise ConnectionError("Transaction error : %s" % ret.text)

        return exchanged_amount


class Accounts(object):
    """ Class to handle the account balances """
    def __init__(self, account_balances):
        self.raw_list = account_balances
        self.list = []
        for account in self.raw_list:
            self.list.append(Amount(currency=account.get("currency"),
                                    revolut_amount=account.get("balance")))

    def __len__(self):
        return len(self.list)

    def __getitem__(self, key):
        """ Méthod to access the object as a list
        (ex : accounts[1]) """
        return self.list[key]

    def csv(self, lang="fr"):
        if lang == "fr":
            csv_str = "Nom du compte;Solde;Devise"
        else:
            csv_str = "Account name,Balance,Currency"

        for account in self.list:
            csv_str += ('\n{currency} wallet,{balance},{currency}'.format(
                    currency=account.currency,
                    balance=account.real_amount_str))
        if lang == "fr":
            # In the French Excel, csv are like "pi;3,14" (not "pi,3.14")
            csv_str = csv_str.replace(",", ";").replace(".", ",")
        return csv_str
