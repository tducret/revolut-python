#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import json
import sys

from datetime import datetime
from datetime import timedelta
from getpass import getpass

from revolut import Revolut, __version__, get_token_step1, get_token_step2


_CLI_DEVICE_ID = 'revolut_cli'
_URL_GET_TRANSACTIONS = 'https://api.revolut.com/user/current/transactions'


@click.command()
@click.option(
    '--token', '-t',
    envvar="REVOLUT_TOKEN",
    type=str,
    help='your Revolut token (or set the env var REVOLUT_TOKEN)',
)
@click.option(
    '--language', '-l',
    type=str,
    help='language ("fr" or "en"), for the csv header and separator',
    default='fr'
)
@click.option(
    '--from_date', '-t',
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help='transactions lookback date in YYYY-MM-DD format (ex: "2019-10-26"). Default 30 days back',
    default=(datetime.now()-timedelta(days=30)).strftime("%Y-%m-%d")
 )
def main(token, language, from_date):
    """ Get the account balances on Revolut """
    if token is None:
        print("You don't seem to have a Revolut token. Use 'revolut_cli' to obtain one")
        sys.exit()

    rev = Revolut(device_id=_CLI_DEVICE_ID, token=token)
    account_transactions = rev.get_account_transactions(from_date)
    print(account_transactions.csv(lang=language))

if __name__ == "__main__":
    main()
