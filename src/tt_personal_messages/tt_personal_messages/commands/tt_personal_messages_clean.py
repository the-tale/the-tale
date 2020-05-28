
import argparse

from tt_web import utils

from .. import service
from .. import operations


parser = argparse.ArgumentParser(description='clean database from removed messages')

parser.add_argument('-c', '--config', metavar='config', required=True, type=str, help='path to config file')


def main():
    args = parser.parse_args()

    config = utils.load_config(args.config)

    async def utility():
        messages_ids = await operations.candidates_to_remove_ids()
        await operations.remove_messages(messages_ids)

    service.run_utility(config, utility)
