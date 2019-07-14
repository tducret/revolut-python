#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import click
from revolut import Revolut, __version__
import revolut_bot
import sys

# Usage : revolutbot.py --help

_CLI_DEVICE_ID = 'revolut_cli'
_BOT_PERCENT_MARGIN = 1  # at least 1% benefit to exchange
_VERBOSE_MODE = False  # can be changed with --verbose parameter

_RETURN_CODE_BUY = 0
_RETURN_CODE_DO_NOT_BUY = 1
_RETURN_CODE_ERROR = 2


@click.command()
@click.option(
    '--token', '-t',
    envvar="REVOLUT_TOKEN",
    type=str,
    help='your Revolut token (or set the env var REVOLUT_TOKEN)',
)
@click.option(
    '--historyfile', '-f',
    type=str,
    help='csv file with the exchange history',
    required=True,
)
@click.option(
    '--forceexchange',
    is_flag=True,
    help='force the exchange, ignoring the bot decision (you may lose money)',
)
@click.option(
    '--simulate', '-s',
    is_flag=True,
    help='do not really exchange your money if set',
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='verbose mode',
)
@click.version_option(
    version=__version__,
    message='%(prog)s, based on [revolut] package version %(version)s'
)
def main(token, simulate, historyfile, verbose, forceexchange):
    if token is None:
        print("You don't seem to have a Revolut token")
        print("Please execute revolut_cli.py first to get one")
        sys.exit(_RETURN_CODE_ERROR)

    global _VERBOSE_MODE
    _VERBOSE_MODE = verbose
    rev = Revolut(device_id=_CLI_DEVICE_ID, token=token)

    to_buy_or_not_to_buy(revolut=rev,
                         simulate=simulate,
                         filename=historyfile,
                         forceexchange=forceexchange)


def log(log_str=""):
    if _VERBOSE_MODE:
        print(log_str)


def to_buy_or_not_to_buy(revolut, simulate, filename, forceexchange):
    percent_margin = _BOT_PERCENT_MARGIN

    last_transactions = revolut_bot.get_last_transactions_from_csv(
                        filename=filename)
    last_tr = last_transactions[-1]  # The last transaction
    log()
    log("Last transaction : {}\n".format(last_tr))
    previous_currency = last_tr.from_amount.currency

    current_balance = last_tr.to_amount  # How much we currently have

    current_balance_in_other_currency = revolut.quote(
                                from_amount=current_balance,
                                to_currency=previous_currency)
    log("Today : {} in {} : {}\n".format(
        current_balance, previous_currency, current_balance_in_other_currency))

    last_sell = last_tr.from_amount  # How much did it cost before selling

    last_sell_plus_margin = revolut_bot.get_amount_with_margin(
                                    amount=last_sell,
                                    percent_margin=percent_margin)
    log("Min value to buy : {} + {}% (margin) = {}\n".format(
        last_sell,
        percent_margin,
        last_sell_plus_margin))

    buy_condition = current_balance_in_other_currency.real_amount > \
        last_sell_plus_margin.real_amount

    if buy_condition or forceexchange:
        if buy_condition:
            log("{} > {}".format(
                current_balance_in_other_currency,
                last_sell_plus_margin))
        elif forceexchange:
            log("/!\\ Force exchange option enabled")
        log("=> BUY")

        if simulate:
            log("(Simulation mode : do not really buy)")
        else:
            exchange_transaction = revolut.exchange(
                            from_amount=current_balance,
                            to_currency=previous_currency,
                            simulate=simulate)
            log("{} bought".format(exchange_transaction.to_amount.real_amount))
            log("Update history file : {}".format(filename))
            revolut_bot.update_historyfile(
                                    filename=filename,
                                    exchange_transaction=exchange_transaction)
        sys.exit(_RETURN_CODE_BUY)
    else:
        log("{} < {}".format(
            current_balance_in_other_currency,
            last_sell_plus_margin))
        log("=> DO NOT BUY")
        sys.exit(_RETURN_CODE_DO_NOT_BUY)


if __name__ == "__main__":
    main()
