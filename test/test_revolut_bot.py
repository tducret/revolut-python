import revolut_bot
from revolut_bot import Transaction
from revolut import Amount
from datetime import datetime
import pytest

# To be tested with : python -m pytest -vs test/test_revolut_bot.py

_AVAILABLE_CURRENCIES = ["USD", "RON", "HUF", "CZK", "GBP", "CAD", "THB",
                         "SGD", "CHF", "AUD", "ILS", "DKK", "PLN", "MAD",
                         "AED", "EUR", "JPY", "ZAR", "NZD", "HKD", "TRY",
                         "QAR", "NOK", "SEK", "BTC", "ETH", "XRP", "BCH",
                         "LTC"]


def test_class_Transaction():
    transaction = Transaction(
                    from_amount=Amount(real_amount=10, currency="USD"),
                    to_amount=Amount(real_amount=8.66, currency="EUR"),
                    date=datetime.strptime("10/07/18 16:30", "%d/%m/%y %H:%M"))

    assert type(transaction) == Transaction
    assert str(transaction) == "(10/07/2018 16:30:00) 10.00 USD => 8.66 EUR"
    print()
    print(transaction)


def test_class_Transaction_errors():
    with pytest.raises(TypeError):
        Transaction(from_amount="10 USD",
                    to_amount=Amount(real_amount=8.66, currency="EUR"),
                    date=datetime.strptime("10/07/18 16:30", "%d/%m/%y %H:%M"))

    with pytest.raises(TypeError):
        Transaction(from_amount=Amount(real_amount=10, currency="USD"),
                    to_amount="8.66 EUR",
                    date=datetime.strptime("10/07/18 16:30", "%d/%m/%y %H:%M"))

    with pytest.raises(TypeError):
        Transaction(from_amount=Amount(real_amount=10, currency="USD"),
                    to_amount=Amount(real_amount=8.66, currency="EUR"),
                    date="10/07/18 16:30")


def test_get_last_transactions_from_csv():
    last_transactions = revolut_bot.get_last_transactions_from_csv(
                        filename="exchange_history_example.csv")
    assert type(last_transactions) == list
    last_tr = last_transactions[-1]
    assert type(last_tr) == Transaction
    print()
    for tr in last_transactions:
        print(tr)


def test_get_last_transactions_from_csv_errors():
    with pytest.raises(FileNotFoundError):
        revolut_bot.get_last_transactions_from_csv(filename="unknown_file.csv")

    with pytest.raises(TypeError):
        revolut_bot.get_last_transactions_from_csv(
            filename="exchange_history_example.csv",
            separator="BAD_SEPARATOR")


# def test_write_a_transaction_to_csv():
#     tr1 = Transaction(from_amount=Amount(real_amount=10, currency="USD"),
#                       to_amount=Amount(real_amount=8.66, currency="EUR"),
#                       date="10/07/18 16:30")
#     tr2 = Transaction(from_amount=Amount(real_amount=8.66, currency="EUR"),
#                       to_amount=Amount(real_amount=10.51, currency="USD"),
#                       date="11/07/18 09:30")
#     revolut_bot.write_a_transaction_to_csv(
#         filename="new_exchange_history.csv")
#     assert revolut_bot.write_a_transaction_to_csv(
#         filename="new_exchange_history.csv")
