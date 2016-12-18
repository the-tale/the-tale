# coding: utf-8

from utg import relations as utg_relations

from the_tale.linguistics.conf import linguistics_settings


def linguistics_context(request): # pylint: disable=W0613
    return {'linguistics_settings': linguistics_settings,
            'UTG_PROPERTY_TYPE': utg_relations.PROPERTY_TYPE}
