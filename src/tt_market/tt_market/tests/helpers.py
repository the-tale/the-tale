import os
import uuid

from tt_web import utils
from tt_web.tests import helpers as web_helpers

from .. import objects
from .. import service
from .. import relations
from .. import operations


class BaseTests(web_helpers.BaseTests):

    def create_application(self):
        return service.create_application(get_config(), loop=self.loop)

    async def clean_environment(self, app=None):
        await operations.clean_database()
        operations.MARKET_INFO_CACHE.hard_reset()


def get_config():
    config_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'config.json')
    return utils.load_config(config_path)


def create_sell_lot(item_type='test.item.type',
                    item_id=None,
                    owner_id=666,
                    price=100500):
    if item_id is None:
        item_id = uuid.uuid4()

    return objects.Lot(type=relations.LOT_TYPE.SELL,
                       item_type=item_type,
                       item_id=item_id,
                       owner_id=owner_id,
                       price=price,
                       created_at=None)


async def prepair_history_log():
    await operations.place_sell_lots([create_sell_lot(item_type='test.1', price=1)])
    await operations.place_sell_lots([create_sell_lot(item_type='test.1', price=1)])
    await operations.close_sell_lot(item_type='test.1', buyer_id=666, price=1, number=1)
    await operations.place_sell_lots([create_sell_lot(item_type='test.1', price=3)])
    await operations.place_sell_lots([create_sell_lot(item_type='test.1', price=4)])
    await operations.cancel_sell_lot(item_type='test.1', owner_id=666, price=3, number=1)
    await operations.place_sell_lots([create_sell_lot(item_type='test.2', price=3)])
    await operations.close_sell_lot(item_type='test.1', buyer_id=666, price=1, number=1)
    await operations.place_sell_lots([create_sell_lot(item_type='test.3', price=4)])
    await operations.place_sell_lots([create_sell_lot(item_type='test.3', price=4)])
    await operations.close_sell_lot(item_type='test.3', buyer_id=666, price=4, number=1)
    await operations.close_sell_lot(item_type='test.2', buyer_id=666, price=3, number=1)
    await operations.close_sell_lot(item_type='test.3', buyer_id=666, price=4, number=1)
