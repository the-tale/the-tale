
import random
import collections

import psycopg2
from psycopg2.extras import Json as PGJson

from tt_web import postgresql as db
from tt_web.common import simple_static_cache

from . import objects
from . import relations
from . import exceptions


async def log(execute, operation_type, lot_type, item_type, item_id, owner_id, price, data):
    await execute('''INSERT INTO log_records (operation_type, lot_type, item_type, item, owner, price, data, created_at)
                     VALUES (%(operation_type)s, %(lot_type)s, %(item_type)s, %(item_id)s, %(owner_id)s, %(price)s, %(data)s, NOW())''',
                  {'operation_type': operation_type.value,
                   'lot_type': lot_type.value,
                   'item_type': item_type,
                   'item_id': item_id,
                   'owner_id': owner_id,
                   'price': price,
                   'data': PGJson(data)})


async def place_sell_lots(lots):
    lots_ids = await db.transaction(_place_sell_lots, {'lots': lots})
    return lots_ids


async def _place_sell_lots(execute, arguments):

    lots = arguments['lots']

    lots_ids = []

    for lot in lots:
        try:
            await execute('''INSERT INTO sell_lots (item_type, item, price, owner, created_at)
                             VALUES (%(item_type)s, %(item)s, %(price)s, %(owner)s, NOW())''',
                          {'item_type': lot.item_type,
                           'item': lot.item_id,
                           'price': lot.price,
                           'owner': lot.owner_id})
            lots_ids.append(lot.item_id)
        except psycopg2.IntegrityError:
            raise exceptions.SellLotForItemAlreadyCreated(item_id=lot.item_id)

        await log(execute,
                  operation_type=relations.OPERATION_TYPE.PLACE_SELL_LOT,
                  lot_type=lot.type,
                  item_type=lot.item_type,
                  item_id=lot.item_id,
                  owner_id=lot.owner_id,
                  price=lot.price,
                  data={})

    MARKET_INFO_CACHE.soft_reset()

    return lots_ids


def _next_candidate_item(candidates):
    owner = random.choice(list(candidates.keys()))
    item = candidates[owner].pop()

    if not candidates[owner]:
        del candidates[owner]

    return item


async def _delete_lots(execute, candidates_ids, number, operation_type, data):

    lots = []

    # In ideal universe we should do candidates_ids.sort() here, to:
    # - prevent intersactions of transactions
    # - guarantee fair processing order
    #
    # But since it is game market, we do other things, to create more interesting gameplay experience.
    # We try to distribute slots choices equally between all players,
    # to ensure that no player can spam market with large amount of lots, to block sells of other players.

    candidates = collections.defaultdict(list)

    for item, owner in candidates_ids:
        candidates[owner].append(item)

    while number > 0:

        if not candidates:
            break

        candidate_id = _next_candidate_item(candidates)

        results = await execute('''DELETE FROM sell_lots WHERE item=%(item)s
                                   RETURNING item_type, item, owner, price, created_at''',
                                {'item': candidate_id})

        if not results:
            continue

        lot = lot_from_row(results[0], type=relations.LOT_TYPE.SELL)

        lots.append(lot)

        number -= 1

        await log(execute,
                  operation_type=operation_type,
                  lot_type=lot.type,
                  item_type=lot.item_type,
                  item_id=lot.item_id,
                  owner_id=lot.owner_id,
                  price=lot.price,
                  data=data)

    if lots:
        MARKET_INFO_CACHE.soft_reset()

    return lots


async def close_sell_lot(item_type, buyer_id, price, number):
    lots = await db.transaction(_close_sell_lot, {'item_type': item_type,
                                                  'buyer_id': buyer_id,
                                                  'price': price,
                                                  'number': number})
    return lots


async def _close_sell_lot(execute, arguments):

    item_type = arguments['item_type']
    buyer_id = arguments['buyer_id']
    price = arguments['price']
    number = arguments['number']

    results = await execute('SELECT item, owner FROM sell_lots WHERE price=%(price)s AND item_type=%(item_type)s',
                            {'price': price, 'item_type': item_type})

    lots = await _delete_lots(execute,
                              candidates_ids=[(row['item'], row['owner']) for row in results],
                              number=number,
                              operation_type=relations.OPERATION_TYPE.CLOSE_SELL_LOT,
                              data={'buyer_id': buyer_id})
    return lots


async def cancel_sell_lot(item_type, owner_id, price, number):
    lots = await db.transaction(_cancel_sell_lot, {'item_type': item_type,
                                                   'price': price,
                                                   'owner_id': owner_id,
                                                   'number': number})
    return lots


async def _cancel_sell_lot(execute, arguments):

    item_type = arguments['item_type']
    owner_id = arguments['owner_id']
    price = arguments['price']
    number = arguments['number']

    results = await execute('SELECT item, owner FROM sell_lots WHERE price=%(price)s AND item_type=%(item_type)s AND owner=%(owner_id)s',
                            {'price': price, 'item_type': item_type, 'owner_id': owner_id})

    lots = await _delete_lots(execute,
                              candidates_ids=[(row['item'], row['owner']) for row in results],
                              number=number,
                              operation_type=relations.OPERATION_TYPE.CANCEL_SELL_LOT,
                              data={})
    return lots


async def load_sell_lots(owner_id):
    results = await db.sql('SELECT * FROM sell_lots WHERE owner=%(owner_id)s',
                           {'owner_id': owner_id})
    return [lot_from_row(row, type=relations.LOT_TYPE.SELL) for row in results]


async def _load_market_info():

    items_summary = []

    results = await db.sql('SELECT item_type, count(*) as sell_number, MIN(price) as min_price, MAX(price) as max_price FROM sell_lots GROUP BY item_type')

    for row in results:
        items_summary.append(objects.ItemTypeSummary(item_type=row['item_type'],
                                                     sell_number=row['sell_number'],
                                                     min_sell_price=row['min_price'],
                                                     max_sell_price=row['max_price'],
                                                     owner_sell_number=0))

    return items_summary


async def get_owner_items_number(owner_id):
    results = await db.sql('SELECT item_type, count(*) as sell_number FROM sell_lots WHERE owner=%(owner_id)s GROUP BY item_type',
                           {'owner_id': owner_id})
    return {row['item_type']: row['sell_number'] for row in results}


async def get_type_prices(item_type):

    results = await db.sql('SELECT price, count(*) as number FROM sell_lots WHERE item_type=%(item_type)s GROUP BY price',
                           {'item_type': item_type})

    return {row['price']: row['number'] for row in results}


async def get_type_prices_for_owner(item_type, owner_id):

    results = await db.sql('SELECT price, count(*) as number FROM sell_lots WHERE item_type=%(item_type)s AND owner=%(owner_id)s GROUP BY price',
                           {'item_type': item_type,
                            'owner_id': owner_id})

    return {row['price']: row['number'] for row in results}


async def load_history_page(page, records_on_page):

    results = await db.sql('''SELECT item_type, price, created_at
                              FROM log_records
                              WHERE operation_type=%(type)s
                              ORDER BY created_at DESC
                              OFFSET %(offset)s
                              LIMIT %(limit)s''',
                           {'type': relations.OPERATION_TYPE.CLOSE_SELL_LOT.value,
                            'offset': (page-1) * records_on_page,
                            'limit': records_on_page})

    return [objects.LogRecord(item_type=row['item_type'],
                              price=row['price'],
                              created_at=row['created_at']) for row in results]


async def history_records_number():
    result = await db.sql('SELECT count(*) as number FROM log_records WHERE operation_type=%(type)s',
                          {'type': relations.OPERATION_TYPE.CLOSE_SELL_LOT.value})
    return result[0]['number']


async def statistics(time_from, time_till):
    data = {'sell_lots_placed': 0,
            'sell_lots_closed': 0,
            'turnover': 0}

    result = await db.sql('''SELECT operation_type, count(*) as count FROM log_records
                             WHERE %(from)s <= created_at AND created_at <= %(till)s
                             GROUP BY operation_type''',
                          {'from': time_from, 'till': time_till})

    for row in result:
        if row['operation_type'] == relations.OPERATION_TYPE.PLACE_SELL_LOT.value:
            data['sell_lots_placed'] = row['count']

        if row['operation_type'] == relations.OPERATION_TYPE.CLOSE_SELL_LOT.value:
            data['sell_lots_closed'] = row['count']

    result = await db.sql('''SELECT SUM(price) as turnover FROM log_records
                             WHERE %(from)s <= created_at AND created_at <= %(till)s AND operation_type=%(operation_type)s
                             GROUP BY operation_type''',
                          {'from': time_from, 'till': time_till, 'operation_type': relations.OPERATION_TYPE.CLOSE_SELL_LOT.value})

    if result:
        data['turnover'] = result[0]['turnover']

    return data


def lot_from_row(row, type):
    return objects.Lot(type=type,
                       item_type=row['item_type'],
                       item_id=row['item'],
                       owner_id=row['owner'],
                       price=row['price'],
                       created_at=row['created_at'])


async def clean_database():
    await db.sql('DELETE FROM log_records')
    await db.sql('DELETE FROM sell_lots')
    MARKET_INFO_CACHE.soft_reset()


class MarketInfoCache(simple_static_cache.BaseCache):
    __slots__ = ()

    def live_time(self):
        return 10**6 # infinity livetime

    async def load_value(self):
        results = await _load_market_info()
        return results


MARKET_INFO_CACHE = MarketInfoCache()
