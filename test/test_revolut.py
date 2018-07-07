import revolut
import pytest

# To best tested with : python -m pytest -vs

_AVAILABLE_CURRENCIES = ["USD", "RON", "HUF", "CZK", "GBP", "CAD", "THB",
                         "SGD", "CHF", "AUD", "ILS", "DKK", "PLN", "MAD",
                         "AED", "EUR", "JPY", "ZAR", "NZD", "HKD", "TRY",
                         "QAR", "NOK", "SEK", "BTC"]


def test_class_Amount():
    amount = revolut.Amount(revolut_amount=100, currency="EUR")
    assert amount.real_amount == 1
    assert str(amount) == "1.00 EUR"
    amount = revolut.Amount(revolut_amount=100000000, currency="BTC")
    assert amount.real_amount == 1
    assert str(amount) == "1.00000000 BTC"
    with pytest.raises(KeyError):
        amount = revolut.Amount(revolut_amount=100, currency="UNKNOWN")
    with pytest.raises(TypeError):
        amount = revolut.Amount(revolut_amount="abc", currency="BTC")
    with pytest.raises(ValueError):
        amount = revolut.Amount(currency="BTC")


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
    btc_to_eur = revolut.Amount(real_amount=1, currency="BTC")
    quote_eur_btc = revolut.quote(
                        from_amount=eur_to_btc,
                        to_currency="BTC")
    quote_btc_eur = revolut.quote(
                        from_amount=btc_to_eur,
                        to_currency="EUR")
    assert type(quote_eur_btc) == revolut.Amount
    assert type(quote_btc_eur) == revolut.Amount
    print()
    print("%s => %s" % (eur_to_btc, quote_eur_btc))
    print("%s => %s" % (btc_to_eur, quote_btc_eur))


def test_exchange():
    assert type(revolut.exchange(
                        from_amount=10.0,
                        from_currency="EUR",
                        to_currency="BTC")) == float
