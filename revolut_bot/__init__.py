# -*- coding: utf-8 -*-
"""
This package allows you to control the Revolut bot
"""

import csv
from revolut import Amount
from datetime import datetime
import io

_CSV_COLUMNS = ["date", "hour", "from_amount", "from_currency",
                "to_amount", "to_currency"]


class Transaction(object):
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


def csv_to_dict(csv_str, separator=","):
    """ From a csv string, returns a list of dictionnaries
>>> csv_to_dict("a,b,c\\n1,2,3")
[{'a': '1', 'b': '2', 'c': '3'}]
>>> csv_to_dict("a,b,c\\n1,2,3\\n4,5,6")
[{'a': '1', 'b': '2', 'c': '3'}, {'a': '4', 'b': '5', 'c': '6'}]
>>> csv_to_dict("a;b;c\\n1;2;3", separator=";")
[{'a': '1', 'b': '2', 'c': '3'}]"""
    dict_list = []
    reader = csv.DictReader(io.StringIO(csv_str), delimiter=separator)
    for line in reader:
        dict_list.append(dict(line))
        # By default, DictReader returns OrderedDict => convert to dict
    return dict_list


def read_file_to_str(filename):
    with open(filename, 'r') as f:
        ret_str = f.read()
    return ret_str


def get_last_transactions_from_csv(filename="exchange_history.csv",
                                   separator=","):
    csv_str = read_file_to_str(filename=filename)
    last_transactions = csv_to_dict(csv_str=csv_str, separator=separator)

    tr_list = []
    for tr in last_transactions:
        tr_obj = dict_transaction_to_Transaction(tr)
        tr_list.append(tr_obj)

    return tr_list


def dict_transaction_to_Transaction(tr_dict):
    """ Converts a transaction dictionnary to a Transaction object """
    if list(tr_dict.keys()) != _CSV_COLUMNS:
        raise TypeError("Columns expected : {}\n{} received".format(
                _CSV_COLUMNS, list(tr_dict.keys())))
    str_date = "{} {}".format(tr_dict["date"],
                              tr_dict["hour"])
    tr = Transaction(from_amount=Amount(
                    real_amount=float(tr_dict["from_amount"]),
                    currency=tr_dict["from_currency"]),
                to_amount=Amount(
                    real_amount=float(tr_dict["to_amount"]),
                    currency=tr_dict["to_currency"]),
                date=datetime.strptime(str_date, "%d/%m/%Y %H:%M:%S"))
    return tr


def write_a_transaction_to_csv(filename):
    return True
