import logging
import argparse
import importlib

from aiohttp import web

from tt_diary import utils


parser = argparse.ArgumentParser(description='Run service')

parser.add_argument('-c', '--config', metavar='config', type=str, help='path to config file')
parser.add_argument('-s', '--service', metavar='service', type=str, help='service module')


def main():
    args = parser.parse_args()

    config = utils.load_config(args.config)

    service_module = importlib.import_module('{}.service'.format(args.service))

    app = service_module.create_application(config)

    logging.info('start service')

    web.run_app(app, port=config['service']['port'])
