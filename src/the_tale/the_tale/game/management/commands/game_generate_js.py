
import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'generate javascript files'

    def handle(self, *args, **options):

        LINGUISTICS_FORMATTERS = {key.value: linguistics_logic.ui_format(key.ui_text)
                                  for key in lexicon_keys.LEXICON_KEY.records
                                  if key.ui_text is not None}

        race_to_text = {}
        for race in relations.RACE.records:
            race_to_text[race.value] = {'male': race.male_text,
                                        'female': race.female_text}

        personality_practical_to_text = {}
        for personality in persons_relations.PERSONALITY_PRACTICAL.records:
            personality_practical_to_text[personality.value] = {'male': personality.male_text,
                                                                'female': personality.female_text}

        personality_cosmetic_to_text = {}
        for personality in persons_relations.PERSONALITY_COSMETIC.records:
            personality_cosmetic_to_text[personality.value] = {'male': personality.male_text,
                                                               'female': personality.female_text}

        with open(conf.settings.JS_CONSTNATS_FILE_LOCATION, 'w') as f:
            f.write(dext_jinja2.render('game/js_constants.js',
                                       context={'actor_type': s11n.to_json({a.name: a.value for a in quests_relations.ACTOR_TYPE.records}),
                                                'gender_to_text': s11n.to_json(dict(relations.GENDER.select('value', 'text'))),
                                                'gender_to_str': s11n.to_json(dict(relations.GENDER.select('value', 'name'))),
                                                'person_type_to_text': s11n.to_json(dict(persons_relations.PERSON_TYPE.select('value', 'text'))),
                                                'race_to_text': s11n.to_json(race_to_text),
                                                'game_state': s11n.to_json(dict(relations.GAME_STATE.select('name', 'value'))),
                                                'ARTIFACT_TYPE': artifacts_relations.ARTIFACT_TYPE,
                                                'NO_EFFECT': artifacts_relations.ARTIFACT_EFFECT.NO_EFFECT,
                                                'EFFECTS': artifacts_effects.EFFECTS,
                                                'ARTIFACT_RARITY': artifacts_relations.RARITY,
                                                'CARD_RARITY': cards_relations.RARITY,
                                                'CARD': cards_types.CARD,
                                                'ABILITY_TYPE': abilities_relations.ABILITY_TYPE,
                                                'SPRITES': map_relations.SPRITES,
                                                'CELL_SIZE': map_conf.settings.CELL_SIZE,
                                                'LINGUISTICS_FORMATTERS': LINGUISTICS_FORMATTERS,
                                                'personality_practical_to_text': personality_practical_to_text,
                                                'personality_cosmetic_to_text': personality_cosmetic_to_text
                                                }))
