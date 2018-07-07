import revolut
import pytest

# To best tested with : python -m pytest -vs

_AVAILABLE_CURRENCIES = ["USD", "RON", "HUF", "CZK", "GBP", "CAD", "THB",
                         "SGD", "CHF", "AUD", "ILS", "DKK", "PLN", "MAD",
                         "AED", "EUR", "JPY", "ZAR", "NZD", "HKD", "TRY",
                         "QAR", "NOK", "SEK", "BTC"]


def test_get_accounts():
    accounts = revolut.get_accounts()
    assert len(accounts) > 0
    print()
    print("%d accounts" % len(accounts))
    for compte in accounts:
        assert type(compte) == dict
        assert type(compte['balance']) == int
        assert compte['currency'] in _AVAILABLE_CURRENCIES
        if compte['currency'] == "BTC":
            balance_format = 8
        else:
            balance_format = 2

        print("%.*f %s" %
              (balance_format,
               revolut.get_real_amount(revolut_amount=compte['balance'],
                                       currency=compte['currency']),
               compte['currency']))


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
    eur_to_btc = 100000
    btc_to_eur = 100000000
    quote_eur_btc = revolut.quote(
                        from_amount=eur_to_btc,
                        from_currency="EUR",
                        to_currency="BTC")
    quote_btc_eur = revolut.quote(
                        from_amount=btc_to_eur,
                        from_currency="BTC",
                        to_currency="EUR")
    assert type(quote_eur_btc) == int
    assert type(quote_btc_eur) == int
    print()
    print("%.2f EUR => %.2f BTC" % (
        revolut.get_real_amount(revolut_amount=eur_to_btc, currency="EUR"),
        revolut.get_real_amount(revolut_amount=quote_eur_btc, currency="BTC")))
    print("%.2f BTC => %.2f EUR" % (
        revolut.get_real_amount(revolut_amount=btc_to_eur, currency="BTC"),
        revolut.get_real_amount(revolut_amount=quote_btc_eur, currency="EUR")))


def test_exchange():
    assert type(revolut.exchange(
                        from_amount=10.0,
                        from_currency="EUR",
                        to_currency="BTC")) == float


def test_get_real_amount():
    real_amount_eur = revolut.get_real_amount(revolut_amount=1, currency="EUR")
    real_amount_btc = revolut.get_real_amount(revolut_amount=1000,
                                              currency="BTC")
    assert real_amount_eur == 0.01
    assert real_amount_btc == 0.00001
    with pytest.raises(KeyError):
        revolut.get_real_amount(revolut_amount=100, currency="UNKNOWN")
    with pytest.raises(TypeError):
        revolut.get_real_amount(revolut_amount="abc", currency="BTC")
