# -*- coding: utf-8 -*-
"""
This package allows you to communicate with your Revolut accounts
"""

import base64
from datetime import datetime
import json
import requests
from urllib.parse import urljoin

__version__ = '0.0.7'  # Should be the same in setup.py

_URL_GET_ACCOUNTS = "https://api.revolut.com/user/current/wallet"
_URL_QUOTE = "https://api.revolut.com/quote/"
_URL_EXCHANGE = "https://api.revolut.com/exchange"
_URL_GET_TOKEN_STEP1 = "https://api.revolut.com/signin"
_URL_GET_TOKEN_STEP2 = "https://api.revolut.com/signin/confirm"

_DEFAULT_TOKEN_FOR_SIGNIN = "QXBwOlM5V1VuU0ZCeTY3Z1dhbjc="

_AVAILABLE_CURRENCIES = ["USD", "RON", "HUF", "CZK", "GBP", "CAD", "THB",
                         "SGD", "CHF", "AUD", "ILS", "DKK", "PLN", "MAD",
                         "AED", "EUR", "JPY", "ZAR", "NZD", "HKD", "TRY",
                         "QAR", "NOK", "SEK", "BTC", "ETH", "XRP", "BCH",
                         "LTC"]

_VAULT_ACCOUNT_TYPE = "SAVINGS"
_ACTIVE_ACCOUNT = "ACTIVE"

# The amounts are stored as integer on Revolut.
# They apply a scale factor depending on the currency
_DEFAULT_SCALE_FACTOR = 100
_SCALE_FACTOR_CURRENCY_DICT = {
                                "EUR": 100,
                                "BTC": 100000000,
                                "ETH": 100000000,
                                "BCH": 100000000,
                                "XRP": 100000000,
                                "LTC": 100000000,
                               }


class Amount:
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
        if self.currency in ["BTC", "ETH", "BCH", "XRP", "LTC"]:
            digits_after_float = 8
        else:
            digits_after_float = 2

        return("%.*f" % (digits_after_float, self.real_amount))

    def __str__(self):
        return('{} {}'.format(self.real_amount_str, self.currency))

    def __repr__(self):
        return("Amount(real_amount={}, currency='{}')".format(
            self.real_amount, self.currency))

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


class Transaction:
    """ Class to handle an exchange transaction """
    def __init__(self, from_amount, to_amount, date):
        if type(from_amount) != Amount:
            raise TypeError
        if type(to_amount) != Amount:
            raise TypeError
        if type(date) != datetime:
            raise TypeError
        self.from_amount = from_amount
        self.to_amount = to_amount
        self.date = date

    def __str__(self):
        return('({}) {} => {}'.format(self.date.strftime("%d/%m/%Y %H:%M:%S"),
                                      self.from_amount,
                                      self.to_amount))


class Client:
    """ Do the requests with the Revolut servers """
    def __init__(self, token, device_id):
        self.session = requests.session()
        self.headers = {
                    'Host': 'api.revolut.com',
                    'X-Api-Version': '1',
                    'X-Device-Id': device_id,
                    'User-Agent': 'Revolut/5.5 500500250 (CLI; Android 4.4.2)',
                    'Authorization': 'Basic '+token,
                    }

    def _get(self, url, expected_status_code=200):
        ret = self.session.get(url=url, headers=self.headers)
        if ret.status_code != expected_status_code:
            raise ConnectionError(
                'Status code {status} for url {url}\n{content}'.format(
                    status=ret.status_code, url=url, content=ret.text))
        return ret

    def _post(self, url, post_data, expected_status_code=200):
        ret = self.session.post(url=url,
                                headers=self.headers,
                                json=post_data)
        if ret.status_code != expected_status_code:
            raise ConnectionError(
                'Status code {status} for url {url}\n{content}'.format(
                    status=ret.status_code, url=url, content=ret.text))
        return ret


class Revolut:
    def __init__(self, token, device_id):
        self.client = Client(token=token, device_id=device_id)

    def get_account_balances(self):
        """ Get the account balance for each currency
        and returns it as a dict {"balance":XXXX, "currency":XXXX} """
        ret = self.client._get(_URL_GET_ACCOUNTS)
        raw_accounts = json.loads(ret.text)

        account_balances = []
        for raw_account in raw_accounts.get("pockets"):
            account_balances.append({
                "balance": raw_account.get("balance"),
                "currency": raw_account.get("currency"),
                "type": raw_account.get("type"),
                "state": raw_account.get("state"),
                # name is present when the account is a vault (type = SAVINGS)
                "vault_name": raw_account.get("name", ""),
            })
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

        data = {
            "fromCcy": from_amount.currency,
            "fromAmount": from_amount.revolut_amount,
            "toCcy": to_currency,
            "toAmount": None,
        }

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
            exchange_transaction = Transaction(from_amount=from_amount,
                                               to_amount=exchanged_amount,
                                               date=datetime.now())
        else:
            raise ConnectionError("Transaction error : %s" % ret.text)

        return exchange_transaction


class Account:
    """ Class to handle an account """
    def __init__(self, account_type, balance, state, vault_name):
        self.account_type = account_type  # CURRENT, SAVINGS
        self.balance = balance
        self.state = state  # ACTIVE, INACTIVE
        self.vault_name = vault_name
        self.name = self.build_account_name()

    def build_account_name(self):
        if self.account_type == _VAULT_ACCOUNT_TYPE:
            account_name = '{currency} {type} ({vault_name})'.format(
                    currency=self.balance.currency,
                    type=self.account_type,
                    vault_name=self.vault_name)
        else:
            account_name = '{currency} {type}'.format(
                    currency=self.balance.currency,
                    type=self.account_type)
        return account_name

    def __str__(self):
        return "{name} : {balance}".format(name=self.name,
                                           balance=str(self.balance))


class Accounts:
    """ Class to handle the account balances """

    def __init__(self, account_balances):
        self.raw_list = account_balances
        self.list = [
            Account(
                account_type=account.get("type"),
                balance=Amount(
                    currency=account.get("currency"),
                    revolut_amount=account.get("balance"),
                ),
                state=account.get("state"),
                vault_name=account.get("vault_name"),
            )
            for account in self.raw_list
        ]

    def get_account_by_name(self, account_name):
        """ Get an account by its name """
        for account in self.list:
            if account.name == account_name:
                return account

    def __len__(self):
        return len(self.list)

    def __getitem__(self, key):
        """ Method to access the object as a list
        (ex : accounts[1]) """
        return self.list[key]

    def csv(self, lang="fr"):
        lang_is_fr = lang == "fr"
        if lang_is_fr:
            csv_str = "Nom du compte;Solde;Devise"
        else:
            csv_str = "Account name,Balance,Currency"

        # Europe uses 'comma' as decimal separator,
        # so it can't be used as delimiter:
        delimiter = ";" if lang_is_fr else ","

        for account in self.list:
            if account.state == _ACTIVE_ACCOUNT:  # Do not print INACTIVE
                csv_str += "\n" + delimiter.join((
                    account.name,
                    account.balance.real_amount_str,
                    account.balance.currency,
                ))

        return csv_str.replace(".", ",") if lang_is_fr else csv_str


def get_token_step1(device_id, phone, password, simulate=False):
    """ Function to obtain a Revolut token (step 1 : send a code by sms) """
    if not simulate:
        c = Client(device_id=device_id, token=_DEFAULT_TOKEN_FOR_SIGNIN)
        data = {"phone": phone, "password": password}
        return c._post(url=_URL_GET_TOKEN_STEP1,
                       json=data,
                       expected_status_code=204)
    return ""


def get_token_step2(device_id, phone, sms_code, simulate=False):
    """ Function to obtain a Revolut token (step 2 : with sms code) """
    if simulate:
        # Because we don't want to receive a code through sms
        # for every test ;)
        simu = '{"user":{"id":"fakeuserid","createdDate":123456789,\
        "address":{"city":"my_city","country":"FR","postcode":"12345",\
        "region":"my_region","streetLine1":"1 rue mon adresse",\
        "streetLine2":"Appt 1"},\"birthDate":[1980,1,1],"firstName":"John",\
        "lastName":"Doe","phone":"+33612345678","email":"myemail@email.com",\
        "emailVerified":false,"state":"ACTIVE","referralCode":"refcode",\
        "kyc":"PASSED","termsVersion":"2018-05-25","underReview":false,\
        "riskAssessed":false,"locale":"en-GB"},"wallet":{"id":"wallet_id",\
        "ref":"12345678","state":"ACTIVE","baseCurrency":"EUR",\
        "topupLimit":3000000,"totalTopup":0,"topupResetDate":123456789,\
        "pockets":[{"id":"pocket_id","type":"CURRENT","state":"ACTIVE",\
        "currency":"EUR","balance":100,"blockedAmount":0,"closed":false,\
        "creditLimit":0}]},"accessToken":"myaccesstoken"}'
        raw_get_token = json.loads(simu)
    else:
        c = Client(device_id=device_id, token=_DEFAULT_TOKEN_FOR_SIGNIN)
        sms_code = sms_code.replace("-", "")  # If the user would put -
        data = {"phone": phone, "code": sms_code}
        ret = c._post(url=_URL_GET_TOKEN_STEP2, post_data=data)
        raw_get_token = json.loads(ret.text)

    user_id = raw_get_token["user"]["id"]
    access_token = raw_get_token["accessToken"]
    token_to_encode = '{}:{}'.format(user_id, access_token).encode('ascii')
    # Ascii encoding required by b64encode function : 8 bits char as input
    token = base64.b64encode(token_to_encode)
    return token.decode('ascii')
