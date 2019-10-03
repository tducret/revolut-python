#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
from getpass import getpass
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
        answer = input("Would you like to generate a token [yes/no]? ")
        selection(answer)
        while True:
            try:
                token = get_token()
            except Exception as e:
                login_error_handler(e)
    else:
        print(token)
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
    password = getpass(
        "What is your Revolut app password [ex: 1234] ? ")
    get_token_step1(
        device_id=_CLI_DEVICE_ID,
        phone=phone,
        password=password
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
    return(token)

def selection(user_input):
    yes_list = ["yes", "ye", "ya", "y", "yeah"]
    no_list = ["no", "nah", "nope", "n"]

    if user_input in yes_list:
        return
    elif user_input in no_list:
        print("Thanks for using the Revolut desktop app!")
        sys.exit()
    else:
        print("Input not recognized.")
        sys.exit()

def login_error_handler(error):
    error_list = {
        "The string supplied did not seem to be a phone number" : "Please check the supplied number and try again.",
        "Status code 401" : "Incorrect login details, please try again.",
        "phone is empty" : "You did not enter a phone number..."
    }
    error = str(error)
    for entry in error_list:
        if entry in error:
            print(error_list.get(entry))
            return
    print("An unknown error has occurred: {}".format(error))
    return

if __name__ == "__main__":
    main()
