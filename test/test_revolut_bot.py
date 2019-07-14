import revolut_bot
from revolut import Amount, Transaction
from datetime import datetime
import pytest
import os

# To be tested with : python -m pytest -vs test/test_revolut_bot.py

_DEVICE_ID = os.environ.get('REVOLUT_DEVICE_ID')
_TOKEN = os.environ.get('REVOLUT_TOKEN')


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


def test_csv_functions():
    _TEST_CSV_FILENAME = "test_file.csv"
    with open(_TEST_CSV_FILENAME, "w") as f:
        f.write("a,b,c\n")
        f.write("1,2,3\n")
        f.write("4,5,6\n")
    csv_str = revolut_bot.read_file_to_str(_TEST_CSV_FILENAME)
    assert csv_str == "a,b,c\n1,2,3\n4,5,6\n"

    csv_dict = revolut_bot.csv_to_dict(csv_str)
    assert csv_dict == [{"a": "1", "b": "2", "c": "3"},
                        {"a": "4", "b": "5", "c": "6"}]

    new_csv_dict = {"a": "7", "b": "8", "c": "9"}
    revolut_bot.append_dict_to_csv(
                        filename=_TEST_CSV_FILENAME,
                        dict_obj=new_csv_dict, separator=",",
                        col_names=["a", "b", "c"])
    csv_str = revolut_bot.read_file_to_str(_TEST_CSV_FILENAME)
    assert csv_str == "a,b,c\n1,2,3\n4,5,6\n7,8,9\n"

    csv_dict = revolut_bot.csv_to_dict(csv_str)
    assert csv_dict == [{"a": "1", "b": "2", "c": "3"},
                        {"a": "4", "b": "5", "c": "6"},
                        {"a": "7", "b": "8", "c": "9"}]

    os.remove(_TEST_CSV_FILENAME)


def test_get_amount_with_margin():
    amount = Amount(real_amount=10, currency="USD")
    percent_margin = 1  # 1%
    amount_with_margin = revolut_bot.get_amount_with_margin(
                                    amount=amount,
                                    percent_margin=percent_margin)
    assert type(amount_with_margin) == Amount
    assert amount_with_margin.real_amount == 10.1
    assert amount_with_margin.currency == "USD"


def test_get_amount_with_margin_errors():
    with pytest.raises(TypeError):
        revolut_bot.get_amount_with_margin(amount=10, percent_margin=1)
    with pytest.raises(TypeError):
        revolut_bot.get_amount_with_margin(
                                amount=Amount(real_amount=10, currency="USD"),
                                percent_margin="1%")


def test_convert_Transaction_to_dict():
    transaction = Transaction(
                    from_amount=Amount(real_amount=10, currency="USD"),
                    to_amount=Amount(real_amount=8.66, currency="EUR"),
                    date=datetime.strptime("10/07/18 16:30", "%d/%m/%y %H:%M"))
    tr_dict = revolut_bot.convert_Transaction_to_dict(transaction)
    assert tr_dict == {'date': '10/07/2018',
                       'from_amount': 10.0,
                       'from_currency': 'USD',
                       'hour': '16:30:00',
                       'to_amount': 8.66,
                       'to_currency': 'EUR'}
