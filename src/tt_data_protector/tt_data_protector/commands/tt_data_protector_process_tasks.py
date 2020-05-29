
import argparse

from tt_web import utils

from .. import logic
from .. import service


parser = argparse.ArgumentParser(description='Process tasks')

parser.add_argument('-c', '--config', metavar='config', required=True, type=str, help='path to config file')


def main():
    args = parser.parse_args()

    config = utils.load_config(args.config)

    async def utility():
        await logic.process_all(config['custom'])

    service.run_utility(config, utility)
