import revolut
import pytest

# To best tested with : python -m pytest -vs

_AVAILABLE_CURRENCIES = ["USD", "RON", "HUF", "CZK", "GBP", "CAD", "THB",
                         "SGD", "CHF", "AUD", "ILS", "DKK", "PLN", "MAD",
                         "AED", "EUR", "JPY", "ZAR", "NZD", "HKD", "TRY",
                         "QAR", "NOK", "SEK", "BTC"]

_SIMU_EXCHANGE = True  # True = Do not execute a real currency exchange


def test_class_Amount():
    amount = revolut.Amount(revolut_amount=100, currency="EUR")
    assert amount.real_amount == 1
    assert str(amount) == "1.00 EUR"

    amount = revolut.Amount(real_amount=1, currency="EUR")
    assert amount.revolut_amount == 100
    assert str(amount) == "1.00 EUR"

    amount = revolut.Amount(revolut_amount=100000000, currency="BTC")
    assert amount.real_amount == 1
    assert str(amount) == "1.00000000 BTC"


def test_class_Amount_errors():
    with pytest.raises(KeyError):
        revolut.Amount(revolut_amount=100, currency="UNKNOWN")

    with pytest.raises(TypeError):
        revolut.Amount(revolut_amount="abc", currency="BTC")

    with pytest.raises(ValueError):
        revolut.Amount(currency="BTC")


def test_get_accounts():
    accounts = revolut.get_accounts()
    assert len(accounts) > 0

    print()
    print("[%d accounts]" % len(accounts))

    for compte in accounts:
        assert type(compte) == dict
        assert type(compte['balance']) == int
        assert compte['currency'] in _AVAILABLE_CURRENCIES

        balance = revolut.Amount(revolut_amount=compte['balance'],
                                 currency=compte['currency'])
        print(balance)


def test_get_last_transaction_from_csv():
    last_tr = revolut.get_last_transaction_from_csv(
        filename="exchange_history.csv")
    assert type(last_tr) == dict
    assert len(last_tr['date'].split("/")) == 3
    assert len(last_tr['hour'].split(":")) == 3
    assert type(last_tr['from_amount']) == float
    assert type(last_tr['to_amount']) == float
    assert last_tr['from_currency'] in _AVAILABLE_CURRENCIES
    assert last_tr['to_currency'] in _AVAILABLE_CURRENCIES


def test_write_a_transaction_to_csv():
    assert revolut.write_a_transaction_to_csv(filename="exchange_history.csv")


def test_quote():
    eur_to_btc = revolut.Amount(real_amount=5508.85, currency="EUR")
    quote_eur_btc = revolut.quote(from_amount=eur_to_btc, to_currency="BTC")
    assert type(quote_eur_btc) == revolut.Amount
    print()
    print("%s => %s" % (eur_to_btc, quote_eur_btc))

    btc_to_eur = revolut.Amount(real_amount=1, currency="BTC")
    quote_btc_eur = revolut.quote(from_amount=btc_to_eur, to_currency="EUR")
    assert type(quote_btc_eur) == revolut.Amount
    print("%s => %s" % (btc_to_eur, quote_btc_eur))


def test_quote_errors():
    with pytest.raises(TypeError):
        revolut.quote(from_amount="100 EUR", to_currency="EUR")

    with pytest.raises(TypeError):
        revolut.quote(from_amount=100, to_currency="EUR")

    with pytest.raises(KeyError):
        eur_to_unknown = revolut.Amount(real_amount=100, currency="EUR")
        revolut.quote(from_amount=eur_to_unknown, to_currency="UNKNOWN")


def test_exchange():
    eur_to_btc = revolut.Amount(real_amount=0.01, currency="EUR")
    exchange_transaction = revolut.exchange(from_amount=eur_to_btc,
                                            to_currency="BTC",
                                            simulate=_SIMU_EXCHANGE)
    assert type(exchange_transaction) == revolut.Amount
    print()
    print("%s => %s : exchange OK" % (eur_to_btc, exchange_transaction))


def test_exchange_errors():
    with pytest.raises(TypeError):
        revolut.exchange(from_amount="100 EUR", to_currency="EUR")

    with pytest.raises(TypeError):
        revolut.exchange(from_amount=100, to_currency="EUR")

    with pytest.raises(KeyError):
        eur_to_unknown = revolut.Amount(real_amount=100, currency="EUR")
        revolut.exchange(from_amount=eur_to_unknown, to_currency="UNKNOWN")

    with pytest.raises(ConnectionError):
        # Should return a status code 400
        one_million_euros = revolut.Amount(real_amount=1000000, currency="EUR")
        revolut.exchange(from_amount=one_million_euros, to_currency="BTC")

    with pytest.raises(ConnectionError):
        # Should return a status code 422 for insufficient funds
        ten_thousands_euros = revolut.Amount(real_amount=10000, currency="AUD")
        revolut.exchange(from_amount=ten_thousands_euros, to_currency="BTC")

    with pytest.raises(ConnectionError):
        # Should return a status code 400 because from and to currencies
        # must be different
        ten_thousands_euros = revolut.Amount(real_amount=1, currency="EUR")
        revolut.exchange(from_amount=ten_thousands_euros, to_currency="EUR")

    with pytest.raises(ConnectionError):
        # Should return a status code 400 because the amount must be > 0
        ten_thousands_euros = revolut.Amount(real_amount=1, currency="EUR")
        revolut.exchange(from_amount=ten_thousands_euros, to_currency="EUR")
