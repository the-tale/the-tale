# coding: utf-8

import urllib2

from dext.utils import s11n

from the_tale.common.utils.conf import utils_settings


def get_currencies_info(base_currency, currencies_list):

    if base_currency not in currencies_list:
        currencies_list.append(base_currency)

    resource = urllib2.urlopen(utils_settings.OPEN_EXCHANGE_RATES_API_LATEST_URL + '?app_id=' + utils_settings.OPEN_EXCHANGE_RATES_API_ID)
    data = s11n.from_json(resource.read())
    resource.close()

    currencies = {}

    for currency in currencies_list:
        currencies[currency] = float(data['rates'][currency]) / data['rates'][base_currency]

    return currencies
