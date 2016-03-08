# coding: utf-8

import os

from the_tale.common.utils import xls

from the_tale.game import relations as game_relations
from the_tale.game.places import modifiers as place_modifiers
from the_tale.game.places import relations as place_relations

from . import relations




_professions_xls_file = os.path.join(os.path.dirname(__file__), 'fixtures/economic.xls')


PROFESSION_TO_RACE = xls.load_table_for_enums(_professions_xls_file, sheet_index=0,
                                              rows_enum=relations.PERSON_TYPE, columns_enum=game_relations.RACE,
                                              data_type=float)

PROFESSION_TO_ECONOMIC = xls.load_table_for_enums_subsets(_professions_xls_file, sheet_index=1,
                                                          rows=relations.PERSON_TYPE.records,
                                                          columns=[place_relations.ATTRIBUTE.PRODUCTION,
                                                                   place_relations.ATTRIBUTE.SAFETY,
                                                                   place_relations.ATTRIBUTE.TRANSPORT,
                                                                   place_relations.ATTRIBUTE.FREEDOM,
                                                                   place_relations.ATTRIBUTE.STABILITY],
                                                          data_type=float)

PROFESSION_TO_ECONOMIC = {relations.PERSON_TYPE(person_type_id): {place_relations.ATTRIBUTE(attribute_id): value
                                                                  for attribute_id, value in person_type_data.iteritems()}
                          for person_type_id, person_type_data in PROFESSION_TO_ECONOMIC.iteritems()}

PROFESSION_TO_SPECIALIZATIONS = xls.load_table_for_enums(_professions_xls_file, sheet_index=2,
                                                         rows_enum=relations.PERSON_TYPE, columns_enum=place_modifiers.CITY_MODIFIERS,
                                                         data_type=float)

PROFESSION_TO_SPECIALIZATIONS = {relations.PERSON_TYPE(person_type_id): {place_modifiers.CITY_MODIFIERS(attribute_id): value
                                                                         for attribute_id, value in person_type_data.iteritems()}
                                 for person_type_id, person_type_data in PROFESSION_TO_SPECIALIZATIONS.iteritems()}
