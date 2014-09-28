# coding: utf-8

from django.db import models

from the_tale.linguistics import relations
from the_tale.linguistics import prototypes

from the_tale.linguistics.lexicon import keys
from the_tale.linguistics.lexicon.groups import relations as groups_relations


def get_templates_count():
    keys_count_data = prototypes.TemplatePrototype._db_filter(state=relations.TEMPLATE_STATE.IN_GAME).values('key').annotate(models.Count('key'))

    keys_count = {key: 0 for key in keys.LEXICON_KEY.records}

    keys_count.update( {keys.LEXICON_KEY(data['key']):  data['key__count']
                        for data in keys_count_data} )

    groups_count = {group: 0 for group in groups_relations.LEXICON_GROUP.records}

    for key, key_count in keys_count.iteritems():
        groups_count[key.group] += key_count

    return groups_count, keys_count
