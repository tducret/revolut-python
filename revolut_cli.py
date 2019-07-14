#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import sys

from revolut import Revolut, __version__, get_token_step1, get_token_step2

# Usage : revolut_cli.py --help

_CLI_DEVICE_ID = 'revolut_cli'


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
    '--account', '-a',
    type=str,
    help='account name (ex : "EUR CURRENT") to get the balance for the account'
 )
@click.version_option(
    version=__version__,
    message='%(prog)s, based on [revolut] package version %(version)s'
)
def main(token, language, account):
    """ Get the account balances on Revolut """
    if token is None:
        print("You don't seem to have a Revolut token")
        answer = input("Would you like to generate a token [yes/no] ? ")
        if answer.lower() in ["y", "yes"]:
            get_token()
            sys.exit()
        else:
            print("OK. Goodbye")
            sys.exit()

    rev = Revolut(device_id=_CLI_DEVICE_ID, token=token)
    account_balances = rev.get_account_balances()
    if account:
        print(account_balances.get_account_by_name(account).balance)
    else:
        print(account_balances.csv(lang=language))


def get_token():
    phone = input(
        "What is your mobile phone (used with your Revolut "
        "account) [ex : +33612345678] ? ")
    password = input(
        "What is your Revolut app password [ex: 1234] ? ")
    get_token_step1(
        device_id=_CLI_DEVICE_ID,
        phone=phone,
        password=password,
    )

    sms_code = input(
        "Please enter the sms code you received [ex : 123456] : ")

    token = get_token_step2(
        device_id=_CLI_DEVICE_ID,
        phone=phone,
        sms_code=sms_code,
    )
    token_str = "Your token is {}".format(token)

    dashes = len(token_str) * "-"
    print("\n".join(("", dashes, token_str, dashes, "")))
    print("You may use it with the --token of this command or set the "
          "environment variable in your ~/.bash_profile or ~/.bash_rc, "
          "for example :", end="\n\n")
    print(">>> revolut_cli.py --token={}".format(token))
    print("or")
    print('echo "export REVOLUT_TOKEN={}" >> ~/.bash_profile'
          .format(token))


if __name__ == "__main__":
    main()
