# -*- coding: utf-8 -*-
import random

MAIN_DESCRIPTION = u''' Герои - основная движущая сила этого мира. Люди, эльфы, орки, троли, гоблины и прочие - каждая расса имеет своих достойных сынов и дочерей, тех, кто выделяется из серой массы как своими возможностями, так и желаниями. Эти единицы формируют сословье героев - тех, кто стоит над мелкими склоками, в которых погрязли остальные обиталели, тех, кто видит дальше и делает больше, тех, кто на равне со своими ангелами творит историю этого мира.  '''

class GameInfoException(Exception): pass

class Attribute(object): pass

class AttributeContainer(object):

    @classmethod
    def attrs(cls):
        result = []
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, type) and issubclass(attr, Attribute):
                result.append(attr)
        return result

class actions:

    class battle(AttributeContainer):

        class strike(Attribute):

            name = u'удар'
            description = u'Атакующий герой бьёт защищающегося'

            class StrikeInfo(object):

                def __init__(self, attaker, defender, damage):
                    self.attaker = attaker
                    self.defender = defender
                    self.damage = damage


            @classmethod
            def do(cls, attaker, defender):
                result = cls.StrikeInfo(attaker=attaker,
                                        defender=defender,
                                        damage=random.randint(attaker.min_damage, attaker.max_damage))
                return result
