# coding: utf-8

from the_tale.game.companions.abilities import container as abilities_container
from the_tale.game.companions.abilities import forms as abilities_forms
from the_tale.game.companions.abilities import effects


FAKE_ABILITIES_CONTAINER_1 = abilities_container.Container(common=(effects.ABILITIES.HEALER, effects.ABILITIES.FAN, effects.ABILITIES.CUTE),
                                                           start=frozenset(),
                                                           coherence=effects.ABILITIES.OBSTINATE,
                                                           honor=None,
                                                           peacefulness=effects.ABILITIES.PEACEFUL)


FAKE_ABILITIES_CONTAINER_2 = abilities_container.Container(common=(effects.ABILITIES.HEALER, effects.ABILITIES.TORTURER),
                                                           start=frozenset((effects.ABILITIES.CLEVER, effects.ABILITIES.CUTE)),
                                                           coherence=effects.ABILITIES.OBSTINATE,
                                                           honor=effects.ABILITIES.HONEST,
                                                           peacefulness=None)



def get_abilities_post_data(abilities, prefix='abilities'):

    widgets_data = abilities_forms.decompress_abilities(abilities)

    data = {'%s_%d' % (prefix, i): value
            for i, value in enumerate(widgets_data)
            if value is not None}

    return data
