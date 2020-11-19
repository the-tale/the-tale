
import logging
import argparse

from tt_web import utils

from .. import service
from .. import objects
from .. import operations


parser = argparse.ArgumentParser(description='')

parser.add_argument('-c', '--config', metavar='config', required=True, type=str, help='path to config file')
parser.add_argument('-a', '--account', metavar='account', required=True, type=int, help='account identifier')
parser.add_argument('-q', '--quantity', metavar='quantity', required=True, type=int, help='amount of currency')


def main():
    args = parser.parse_args()

    config = utils.load_config(args.config)

    async def utility():
        account_info = await operations.load_account_info(args.account)

        if account_info is None:
            logging.error('Can not find account info. It MUST be created manually. Try to open payment interface in client.')
            return

        invoice = objects.Invoice(xsolla_id=None,
                                  account_id=account_info.id,
                                  is_fake=True,
                                  data={'xsolla': {'purchase': {'virtual_currency': {'quantity': args.quantity}},
                                                   'transaction': {}}})

        result = await operations.register_invoice(invoice)

        logging.info('result: %s', result)

    service.run_utility(config, utility)
