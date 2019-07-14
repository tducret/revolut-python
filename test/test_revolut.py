from revolut import Amount, Accounts, Account, Transaction, Revolut, Client
from revolut import get_token_step1, get_token_step2
import pytest
import os

# To be tested with : python -m pytest -vs test/test_revolut.py

_AVAILABLE_CURRENCIES = ["USD", "RON", "HUF", "CZK", "GBP", "CAD", "THB",
                         "SGD", "CHF", "AUD", "ILS", "DKK", "PLN", "MAD",
                         "AED", "EUR", "JPY", "ZAR", "NZD", "HKD", "TRY",
                         "QAR", "NOK", "SEK", "BTC", "ETH", "XRP", "BCH",
                         "LTC"]

_DEVICE_ID = os.environ.get('REVOLUT_DEVICE_ID')
_TOKEN = os.environ.get('REVOLUT_TOKEN')

_SIMU_EXCHANGE = True  # True = Do not execute a real currency exchange
_SIMU_GET_TOKEN = True  # True = Do not try to get a real token
# (sms reception involved)
if _SIMU_GET_TOKEN is True:
    _PHONE = "+33612345678"
    _PASSWORD = "1234"
else:
    _PHONE = os.environ.get('REVOLUT_PHONE')
    _PASSWORD = os.environ.get('REVOLUT_TOKEN')

revolut = Revolut(token=_TOKEN, device_id=_DEVICE_ID)


def test_class_Amount():
    amount = Amount(revolut_amount=100, currency="EUR")
    assert amount.real_amount == 1
    assert str(amount) == "1.00 EUR"

    amount = Amount(real_amount=1, currency="EUR")
    assert amount.revolut_amount == 100
    assert str(amount) == "1.00 EUR"

    amount = Amount(revolut_amount=100000000, currency="BTC")
    assert amount.real_amount == 1
    assert str(amount) == "1.00000000 BTC"


def test_class_Amount_errors():
    with pytest.raises(KeyError):
        Amount(revolut_amount=100, currency="UNKNOWN")

    with pytest.raises(TypeError):
        Amount(revolut_amount="abc", currency="BTC")

    with pytest.raises(TypeError):
        Amount(real_amount="def", currency="EUR")

    with pytest.raises(ValueError):
        Amount(currency="BTC")


def test_get_account_balances():
    accounts = revolut.get_account_balances()
    assert len(accounts) > 0

    print()
    print('[{} accounts]'.format(len(accounts)))

    for account in accounts:
        assert type(account) == Account
        print('{}'.format(account))


def test_quote():
    eur_to_btc = Amount(real_amount=5508.85, currency="EUR")
    quote_eur_btc = revolut.quote(from_amount=eur_to_btc, to_currency="BTC")
    assert type(quote_eur_btc) == Amount
    print()
    print('{} => {}'.format(eur_to_btc, eur_to_btc))

    btc_to_eur = Amount(real_amount=1, currency="BTC")
    quote_btc_eur = revolut.quote(from_amount=btc_to_eur, to_currency="EUR")
    assert type(quote_btc_eur) == Amount
    print('{} => {}'.format(btc_to_eur, quote_btc_eur))


def test_quote_commission():
    currency1 = "USD"
    currency2 = "EUR"
    step1 = Amount(real_amount=5000, currency=currency1)
    step2 = revolut.quote(from_amount=step1, to_currency=currency2)
    step3 = revolut.quote(from_amount=step2, to_currency=currency1)
    print()
    comm_rate = 1-(step3.real_amount/step1.real_amount)
    print('Commission {}<->{} {:.2%}'.format(currency1, currency2, comm_rate))
    assert comm_rate < 0.05


def test_quote_errors():
    with pytest.raises(TypeError):
        revolut.quote(from_amount="100 EUR", to_currency="EUR")

    with pytest.raises(TypeError):
        revolut.quote(from_amount=100, to_currency="EUR")

    with pytest.raises(KeyError):
        eur_to_unknown = Amount(real_amount=100, currency="EUR")
        revolut.quote(from_amount=eur_to_unknown, to_currency="UNKNOWN")


def test_exchange():
    eur_to_btc = Amount(real_amount=0.01, currency="EUR")
    exchange_transaction = revolut.exchange(from_amount=eur_to_btc,
                                            to_currency="BTC",
                                            simulate=_SIMU_EXCHANGE)
    assert type(exchange_transaction) == Transaction
    print()
    print('{} => {} : exchange OK'.format(eur_to_btc, exchange_transaction))


def test_exchange_errors():
    with pytest.raises(TypeError):
        revolut.exchange(from_amount="100 EUR", to_currency="EUR")

    with pytest.raises(TypeError):
        revolut.exchange(from_amount=100, to_currency="EUR")

    with pytest.raises(KeyError):
        eur_to_unknown = Amount(real_amount=100, currency="EUR")
        revolut.exchange(from_amount=eur_to_unknown, to_currency="UNKNOWN")

    with pytest.raises(ConnectionError):
        # Should return a status code 400
        one_million_euros = Amount(real_amount=1000000, currency="EUR")
        revolut.exchange(from_amount=one_million_euros, to_currency="BTC")

    with pytest.raises(ConnectionError):
        # Should return a status code 422 for insufficient funds
        ten_thousands_euros = Amount(real_amount=10000, currency="AUD")
        revolut.exchange(from_amount=ten_thousands_euros, to_currency="BTC")

    with pytest.raises(ConnectionError):
        # Should return a status code 400 because from and to currencies
        # must be different
        ten_thousands_euros = Amount(real_amount=1, currency="EUR")
        revolut.exchange(from_amount=ten_thousands_euros, to_currency="EUR")

    with pytest.raises(ConnectionError):
        # Should return a status code 400 because the amount must be > 0
        ten_thousands_euros = Amount(real_amount=1, currency="EUR")
        revolut.exchange(from_amount=ten_thousands_euros, to_currency="EUR")


def test_class_account():
    account = Account(account_type="CURRENT",
                      balance=Amount(real_amount=200.85, currency="EUR"),
                      state="ACTIVE",
                      vault_name="")
    assert account.name == "EUR CURRENT"
    assert str(account) == "EUR CURRENT : 200.85 EUR"

    vault = Account(account_type="SAVINGS",
                    balance=Amount(real_amount=150.35, currency="USD"),
                    state="ACTIVE",
                    vault_name="My vault")
    assert vault.name == "USD SAVINGS (My vault)"
    assert str(vault) == "USD SAVINGS (My vault) : 150.35 USD"


def test_class_accounts():
    account_dicts = [{"balance": 10000, "currency": "EUR",
                      "type": "CURRENT", "vault_name": "", "state": "ACTIVE"},
                     {"balance": 550, "currency": "USD",
                      "type": "CURRENT", "vault_name": "", "state": "ACTIVE"},
                     {"balance": 0, "currency": "GBP", "vault_name": "",
                      "type": "CURRENT", "state": "INACTIVE"},
                     {"balance": 1000000, "currency": "BTC",
                      "type": "CURRENT", "vault_name": "", "state": "ACTIVE"},
                     {"balance": 1000, "currency": "EUR",
                      "vault_name": "My vault",
                      "type": "SAVINGS", "state": "ACTIVE"}]

    accounts = Accounts(account_dicts)
    assert len(accounts.list) == 5
    assert type(accounts[0]) == Account

    csv_fr = accounts.csv(lang="fr")
    print(csv_fr)
    assert csv_fr == "Nom du compte;Solde;Devise\n\
EUR CURRENT;100,00;EUR\n\
USD CURRENT;5,50;USD\n\
BTC CURRENT;0,01000000;BTC\n\
EUR SAVINGS (My vault);10,00;EUR"

    csv_en = accounts.csv(lang="en")
    print(csv_en)
    assert csv_en == "Account name,Balance,Currency\n\
EUR CURRENT,100.00,EUR\n\
USD CURRENT,5.50,USD\n\
BTC CURRENT,0.01000000,BTC\n\
EUR SAVINGS (My vault),10.00,EUR"

    account = accounts.get_account_by_name("BTC CURRENT")
    print(account)
    assert type(account) == Account

    account = accounts.get_account_by_name("Not existing")
    assert account is None


def test_client_errors():
    with pytest.raises(ConnectionError):
        c = Client(device_id="unknown", token="unknown")
        c._get("https://api.revolut.com/unknown_page")


def test_get_token(capsys):
    _DEVICE_ID_TEST = "cli"
    get_token_step1(device_id=_DEVICE_ID_TEST,
                    phone=_PHONE,
                    password=_PASSWORD,
                    simulate=_SIMU_GET_TOKEN)

    if _SIMU_GET_TOKEN is True:
        sms_code = "123456"
    else:
        with capsys.disabled():
            print()
            sms_code = input(
                "Please enter the sms code sent to {} : ".format(_PHONE))

    token = get_token_step2(device_id=_DEVICE_ID_TEST,
                            phone=_PHONE,
                            sms_code=sms_code,
                            simulate=_SIMU_GET_TOKEN)
    assert token != ""
    print()
    print("Your token is {}".format(token))

    if _SIMU_GET_TOKEN is not True:
        new_revolut = Revolut(token=token, device_id=_DEVICE_ID_TEST)

        accounts = new_revolut.get_account_balances()
        assert len(accounts) > 0

        print()
        print('[{} accounts]'.format(len(accounts)))

        for account in accounts:
            assert type(account) == Amount
            print('{}'.format(account))
