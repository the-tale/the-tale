
import smart_imports

smart_imports.all()


BASE_ATTRIBUTES = [places_relations.ATTRIBUTE.PRODUCTION,
                   places_relations.ATTRIBUTE.SAFETY,
                   places_relations.ATTRIBUTE.TRANSPORT,
                   places_relations.ATTRIBUTE.FREEDOM,
                   places_relations.ATTRIBUTE.CULTURE,
                   places_relations.ATTRIBUTE.STABILITY]


_professions_xls_file = os.path.join(os.path.dirname(__file__), 'fixtures/economic.xls')


PROFESSION_TO_RACE = utils_xls.load_table_for_enums(_professions_xls_file, sheet_index=0,
                                                    rows_enum=relations.PERSON_TYPE, columns_enum=game_relations.RACE,
                                                    data_type=float)

PROFESSION_TO_ECONOMIC = utils_xls.load_table_for_enums_subsets(_professions_xls_file, sheet_index=1,
                                                                rows=relations.PERSON_TYPE.records,
                                                                columns=BASE_ATTRIBUTES,
                                                                data_type=float)

PROFESSION_TO_ECONOMIC = {relations.PERSON_TYPE(person_type_id): {places_relations.ATTRIBUTE(attribute_id): value
                                                                  for attribute_id, value in person_type_data.items()}
                          for person_type_id, person_type_data in PROFESSION_TO_ECONOMIC.items()}

PROFESSION_TO_SPECIALIZATIONS = utils_xls.load_table_for_enums(_professions_xls_file, sheet_index=2,
                                                               rows_enum=relations.PERSON_TYPE, columns_enum=places_modifiers.CITY_MODIFIERS,
                                                               data_type=float)

PROFESSION_TO_SPECIALIZATIONS = {relations.PERSON_TYPE(person_type_id): {places_modifiers.CITY_MODIFIERS(attribute_id): value
                                                                         for attribute_id, value in person_type_data.items()}
                                 for person_type_id, person_type_data in PROFESSION_TO_SPECIALIZATIONS.items()}
