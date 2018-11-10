
import smart_imports

smart_imports.all()


EXPECTED_RESTRICTIONS = {
    restrictions.GROUP.GENDER: [record.value for record in game_relations.GENDER.records],
    restrictions.GROUP.RACE: [record.value for record in game_relations.RACE.records],
    restrictions.GROUP.HABIT_HONOR: [game_relations.HABIT_HONOR_INTERVAL.LEFT_1.value,
                                     game_relations.HABIT_HONOR_INTERVAL.RIGHT_1.value],
    restrictions.GROUP.HABIT_PEACEFULNESS: [game_relations.HABIT_PEACEFULNESS_INTERVAL.LEFT_1.value,
                                            game_relations.HABIT_PEACEFULNESS_INTERVAL.RIGHT_1.value],
    restrictions.GROUP.ARCHETYPE: [record.value for record in game_relations.ARCHETYPE.records],
    restrictions.GROUP.UPBRINGING: [record.value for record in tt_beings_relations.UPBRINGING.records],
    restrictions.GROUP.FIRST_DEATH: [record.value for record in tt_beings_relations.FIRST_DEATH.records],
    restrictions.GROUP.AGE: [record.value for record in tt_beings_relations.AGE.records]}


def print_missed_restrictions(required_restrictions):
    print()
    print('missed restrictions:')

    results = []

    for restrictions_group in required_restrictions:
        results.append(' + '.join(group.text + ': ' + group.static_relation(external_id).text
                                  for group, external_id in sorted(restrictions_group, key=lambda x: (x[0].value, x[1]))))

    if not results:
        print('missed restrictions: no')
        return

    print('missed restrictions: {}'.format(len(results)))

    for result in sorted(results):
        print(result)


def test_minimum_filled(templates_restrictions, groups):
    product_source = [[(group, external_id) for external_id in EXPECTED_RESTRICTIONS[group]]
                      for group in groups]

    required_restrictions = set(frozenset(tuple(x) for x in combination)
                                for combination in itertools.product(*product_source))

    print('required', len(required_restrictions))

    for full_restrictions in templates_restrictions:
        removed_restriction = {(group, external_id)
                               for group, external_id in full_restrictions
                               if group in groups}

        if removed_restriction in required_restrictions:
            required_restrictions.remove(removed_restriction)

    print_missed_restrictions(required_restrictions)


class Command(django_management.BaseCommand):

    help = 'search missed history templates'

    def handle(self, *args, **options):

        restr = {}

        for key, ts in storage.lexicon.item._data.items():
            if not key.group.is_HERO_HISTORY:
                continue
            restr[key] = [frozenset((storage.restrictions[r].group, storage.restrictions[r].external_id) for v, r in rs)
                          for t, rs in ts]

        test_minimum_filled(templates_restrictions=restr[keys.LEXICON_KEY.HERO_HISTORY_BIRTH],
                            groups=[restrictions.GROUP.RACE,
                                    restrictions.GROUP.GENDER])

        test_minimum_filled(templates_restrictions=restr[keys.LEXICON_KEY.HERO_HISTORY_CHILDHOOD],
                            groups=[restrictions.GROUP.UPBRINGING,
                                    restrictions.GROUP.HABIT_HONOR,
                                    restrictions.GROUP.HABIT_PEACEFULNESS])

        test_minimum_filled(templates_restrictions=restr[keys.LEXICON_KEY.HERO_HISTORY_DEATH],
                            groups=[restrictions.GROUP.GENDER,
                                    restrictions.GROUP.AGE,
                                    restrictions.GROUP.ARCHETYPE,
                                    restrictions.GROUP.FIRST_DEATH])
