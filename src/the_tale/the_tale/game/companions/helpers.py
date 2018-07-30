
import smart_imports

smart_imports.all()


FAKE_ABILITIES_CONTAINER_1 = companions_abilities_container.Container(common=(companions_abilities_effects.ABILITIES.HEALER, companions_abilities_effects.ABILITIES.FAN, companions_abilities_effects.ABILITIES.CUTE),
                                                                      start=frozenset(),
                                                                      coherence=companions_abilities_effects.ABILITIES.OBSTINATE,
                                                                      honor=None,
                                                                      peacefulness=companions_abilities_effects.ABILITIES.PEACEFUL)


FAKE_ABILITIES_CONTAINER_2 = companions_abilities_container.Container(common=(companions_abilities_effects.ABILITIES.HEALER, companions_abilities_effects.ABILITIES.TORTURER),
                                                                      start=frozenset((companions_abilities_effects.ABILITIES.CLEVER, companions_abilities_effects.ABILITIES.CUTE)),
                                                                      coherence=companions_abilities_effects.ABILITIES.OBSTINATE,
                                                                      honor=companions_abilities_effects.ABILITIES.HONEST,
                                                                      peacefulness=None)


def get_abilities_post_data(abilities, prefix='abilities'):

    widgets_data = companions_abilities_forms.decompress_abilities(abilities)

    data = {'%s_%d' % (prefix, i): value
            for i, value in enumerate(widgets_data)
            if value is not None}

    return data


RARITIES_ABILITIES = {relations.RARITY.COMMON: companions_abilities_container.Container(start=(companions_abilities_effects.ABILITIES.WISE,)),
                      relations.RARITY.UNCOMMON: companions_abilities_container.Container(start=(companions_abilities_effects.ABILITIES.WISE, companions_abilities_effects.ABILITIES.UNCOMMON,)),
                      relations.RARITY.RARE: companions_abilities_container.Container(start=(companions_abilities_effects.ABILITIES.WISE, companions_abilities_effects.ABILITIES.RARE,)),
                      relations.RARITY.EPIC: companions_abilities_container.Container(start=(companions_abilities_effects.ABILITIES.WISE, companions_abilities_effects.ABILITIES.RARE, companions_abilities_effects.ABILITIES.CAMOUFLAGE)),
                      relations.RARITY.LEGENDARY: companions_abilities_container.Container(start=(companions_abilities_effects.ABILITIES.SPECIAL,))}
