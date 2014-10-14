# coding: utf-8

from the_tale.linguistics.conf import linguistics_settings


def linguistics_context(request): # pylint: disable=W0613
    return {'linguistics_settings': linguistics_settings}
