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

    class trading(AttributeContainer):

        class trade_in_town(Attribute):

            name = u'торговля в городе'
            description = u'торговля в городе'

            @classmethod
            def sell_price(cls, seller, artifact, selling_crit):
                left_delta = int(artifact.cost * 0.85)
                right_delta = int(artifact.cost * 1.15)
                price = random.randint(left_delta, right_delta)
                if selling_crit == 1:
                    price = int(price * 1.5)
                elif selling_crit == -1:
                    price = max(1, int(price * 0.75))
                return price

    class equipping(AttributeContainer):

        class equip_in_town(Attribute):
            name = u'экипировка в городе'
            description = u'управление обмундированием в городе'

            @classmethod
            def equip(cls, hero):

                from .bag import can_equip, ARTIFACT_TYPES_TO_SLOTS
                equipped = None
                unequipped = None
                for uuid, artifact in hero.bag.items():
                    if not can_equip(artifact) or artifact.equip_type is None:
                        continue

                    for slot in ARTIFACT_TYPES_TO_SLOTS[artifact.equip_type]:
                        equipped_artifact = hero.equipment.get(slot)
                        if equipped_artifact is None:
                            equipped = True
                            hero.bag.pop_artifact(artifact)
                            hero.equipment.equip(slot, artifact)
                            equipped = artifact
                            break

                    if equipped:
                        break

                    for slot in ARTIFACT_TYPES_TO_SLOTS[artifact.equip_type]:
                        equipped_artifact = hero.equipment.get(slot)
                        if equipped_artifact.total_points_spent < artifact.total_points_spent:
                            equipped = True
                            hero.bag.pop_artifact(artifact)
                            hero.equipment.unequip(slot)
                            hero.bag.put_artifact(equipped_artifact)
                            hero.equipment.equip(slot, artifact)
                            equipped = artifact
                            unequipped = equipped_artifact
                            break

                    if equipped:
                        break

                return unequipped, equipped


class needs:

    class InTown(AttributeContainer):

        class equipping(Attribute):

            name = u'необходимость смены экипировки'
            description = u'необходимо ли герою поменять снаряжение'

            @classmethod
            def check(cls, hero):
                from .bag import can_equip
                return any( can_equip(artifact) for uuid, artifact in hero.bag.items() )
