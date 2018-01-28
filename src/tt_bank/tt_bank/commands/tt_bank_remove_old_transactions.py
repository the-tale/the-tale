
import argparse

from tt_web import utils

from .. import service
from .. import operations


parser = argparse.ArgumentParser(description='Run service')

parser.add_argument('-c', '--config', metavar='config', required=True, type=str, help='path to config file')
parser.add_argument('-t', '--timeout', metavar='timeout', required=True, type=int, help='timeout from now when we can remove transaction (in seconds)')


def main():
    args = parser.parse_args()

    config = utils.load_config(args.config)

    async def utility(loop):
        await operations.remove_old_transactions(timeout=args.timeout)

    service.run_utility(config, utility)
