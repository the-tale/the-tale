# -*- coding: utf-8 -*-
import random

MAIN_DESCRIPTION = u''' Герои - основная движущая сила этого мира. Люди, эльфы, орки, троли, гоблины и прочие - каждая расса имеет своих достойных сынов и дочерей, тех, кто выделяется из серой массы как своими возможностями, так и желаниями. Эти единицы формируют сословье героев - тех, кто стоит над мелкими склоками, в которых погрязли остальные обиталели, тех, кто видит дальше и делает больше, тех, кто на равне со своими ангелами творит историю этого мира.  '''

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


class attributes:

    class base(AttributeContainer):
        class wisdom(Attribute): 
            initial = 1
            name = u'wisdom'
            description = u'Мера мудрости героя, изначально для всех героев равна 1, растёт со временем (по мере выполнения квестов), влияет на точность действий, открывает новые ходы в заданиях, так же влияет на влияние, оказываемое героем на окружающую среду.'


    class primary(AttributeContainer):

        TOTAL_POINTS = 5+4+3+2 
        FREE_POINTS = 5+4+3+2 - 4

        class intellect(Attribute): 
            initial = (1, 5) 
            name = u'intellect' 
            description = u'Характеризует скорость обучения героя, скорость решения загадок и принятия прочих решений, открывает ходы в квестах, влияет на критический урон, скрость прочтения заклинаний'

        class constitution(Attribute): 
            initial = (1, 5) 
            name = u'constitution' 
            description = u'Телосложение героя, влияет на его здоровье и физическую силу и, соответственно, повреждения в бою'

        class reflexes(Attribute): 
            initial = (1, 5) 
            name = u'reflexes'
            description = u'Рефлексы, скорость реакции, влияет на очередность действий в бою, успешность комбо приёмов, уклонение и прочую защиту'

        class chaoticity(Attribute): 
            initial = (1, 5) 
            name = u'chaoticity' 
            description = u'Мера хаотичности героя, чем больше, тем чаще с ним будут происходить экстроардинарные события: критически попадая по нему/им, промахи, встречи, особый лут'

    
    class secondary(AttributeContainer): 

        class move_speed(Attribute):

            name = u'move speed'
            description = u'Скорость передвижения героя по карте (км/ход)'

            @classmethod
            def get(cls, hero):
                return (0.5 + hero.constitution * 0.2) / 5

        class battle_speed(Attribute):

            name = u'move speed'
            description = u'Скорость действий героя в бою, чем больше - тем лучше'

            @classmethod
            def get(cls, hero):
                return hero.reflexes + hero.constitution / 2 + hero.intellect / 5

        class max_health(Attribute):

            name = u'max_health'
            description = u'Максимальный запас здоровья героя'

            @classmethod
            def get(cls, hero):
                return cls.from_attrs(hero.constitution, hero.wisdom)

            @classmethod
            def from_attrs(cls, constitution, wisdom):
                return 25 + constitution * 10 + wisdom

        class min_damage(Attribute):
            name = u'min_damage'
            description = u'Минимальный урон, наносимый героем'

            @classmethod
            def get(cls, hero):
                return max(1, int((hero.constitution * 2 + hero.reflexes * 2 + hero.intellect) / 3.0 - hero.chaoticity) )

        class max_damage(Attribute):
            name = u'max_damage'
            description = u'Максимальный урон, наносимый героем'

            @classmethod
            def get(cls, hero):
                return int((hero.constitution * 2 + hero.reflexes * 2 + hero.intellect) / 3.0 + hero.chaoticity)

        class bag_size(Attribute):

            name = u'bag size'
            description = u'Максимальная вместимость рюкзака'

            @classmethod
            def get(cls, hero):
                return int(5 + hero.constitution + hero.wisdom/10) 

    class accumulated(AttributeContainer):
        pass



class actions:

    class battle(AttributeContainer):

        class strike(Attribute):

            name = u'strike'
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
