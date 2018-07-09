#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import click
from revolut import Revolut, __version__

# Use
# revolut.py --deviceid <device_id> --token <token>
# revolut.py (with environment variables set :
# REVOLUT_DEVICE_ID, REVOLUT_TOKEN)


@click.command()
@click.option(
    '--deviceid', '-d',
    envvar="REVOLUT_DEVICE_ID",
    type=str,
    help='your device id',
    prompt='your device id'
)
@click.option(
    '--token', '-t',
    envvar="REVOLUT_TOKEN",
    type=str,
    help='your Revolut token',
    prompt='your Revolut token'
)
@click.option(
    '--token', '-t',
    envvar="REVOLUT_TOKEN",
    type=str,
    help='your Revolut token',
    prompt='your Revolut token'
)
@click.option(
    '--language', '-l',
    type=str,
    help='csv output language ("fr" or "en")',
    default='fr'
)
@click.version_option(
    version=__version__,
    message='%(prog)s, based on [revolut] package version %(version)s'
)
def main(deviceid, token, language):
    """ Get the account balances on Revolut """
    rev = Revolut(device_id=deviceid, token=token)
    account_balances = rev.get_account_balances()

    print(account_balances.csv(lang=language))


if __name__ == "__main__":
    main()
