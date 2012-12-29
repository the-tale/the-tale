# coding: utf-8

from game.heroes.habilities.prototypes import AbilityPrototype, ABILITY_TYPE, ABILITY_ACTIVATION_TYPE

class AbilityModifiersBase(AbilityPrototype):

    INCOMING_MAGIC_DAMAGE_MODIFIER = [1, 1, 1, 1, 1]
    INCOMING_PHYSIC_DAMAGE_MODIFIER = [1, 1, 1, 1, 1]

    OUTCOMING_MAGIC_DAMAGE_MODIFIER = [1, 1, 1, 1, 1]
    OUTCOMING_PHYSIC_DAMAGE_MODIFIER = [1, 1, 1, 1, 1]

    @property
    def incoming_magic_damage_modifier(self): return self.INCOMING_MAGIC_DAMAGE_MODIFIER[self.level-1]

    @property
    def incoming_physic_damage_modifier(self): return self.INCOMING_PHYSIC_DAMAGE_MODIFIER[self.level-1]

    @property
    def outcoming_magic_damage_modifier(self): return self.OUTCOMING_MAGIC_DAMAGE_MODIFIER[self.level-1]

    @property
    def outcoming_physic_damage_modifier(self): return self.OUTCOMING_PHYSIC_DAMAGE_MODIFIER[self.level-1]

    def update_context(self, actor, enemy):
        actor.context.use_incoming_damage_modifier(self.incoming_physic_damage_modifier, self.incoming_magic_damage_modifier)
        actor.context.use_outcoming_damage_modifier(self.outcoming_physic_damage_modifier, self.outcoming_magic_damage_modifier)


class MAGE(AbilityModifiersBase):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE

    NAME = u'Маг'
    normalized_name = NAME
    DESCRIPTION = u'Маг всё своё усердие направляет в совершенствование магических умений, поэтому имеет увеличеный магический урон, защиту от магии и уменьшенные физический урон и защиту от физических атак.'

    INCOMING_MAGIC_DAMAGE_MODIFIER = [0.94, 0.89, 0.85, 0.8, 0.75]
    INCOMING_PHYSIC_DAMAGE_MODIFIER = [1.025, 1.04, 1.075, 1.1, 1.125]

    OUTCOMING_MAGIC_DAMAGE_MODIFIER = [1.07, 1.11, 1.15, 1.2, 1.25]
    OUTCOMING_PHYSIC_DAMAGE_MODIFIER = [0.975, 0.96, 0.925, 0.9, 0.875]


class WARRIOR(AbilityModifiersBase):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE

    NAME = u'Воин'
    normalized_name = NAME
    DESCRIPTION = u'Воин большинство времени тратит на физические тренировки, благодаря чему наносит больший физический урон, имеет хорошую защиту от физических атак, но слабо противостоит магическим атакам и сам с трудом пользуется магией.'

    INCOMING_MAGIC_DAMAGE_MODIFIER =   [1.025, 1.04, 1.070, 1.1, 1.125]
    INCOMING_PHYSIC_DAMAGE_MODIFIER =  [0.940, 0.90, 0.830, 0.8, 0.750]

    OUTCOMING_MAGIC_DAMAGE_MODIFIER =  [0.975, 0.95, 0.925, 0.9, 0.875]
    OUTCOMING_PHYSIC_DAMAGE_MODIFIER = [1.060, 1.14, 1.170, 1.2, 1.250]


class GARGOYLE(AbilityModifiersBase):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE

    NAME = u'Горгулья'
    normalized_name = NAME
    DESCRIPTION = u'Подобно горгулье, обладатель этой способности имеет увеличенную защиту от всех типов атак.'

    INCOMING_MAGIC_DAMAGE_MODIFIER = [0.960, 0.940, 0.925, 0.900, 0.875]
    INCOMING_PHYSIC_DAMAGE_MODIFIER = [0.960, 0.940, 0.925, 0.900, 0.875]


class KILLER(AbilityModifiersBase):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE

    NAME = u'Убийца'
    normalized_name = NAME
    DESCRIPTION = u'Ориентируясь на быстрый бой, убийца совершенствует свои атакующие способности в ущерб защитным.'

    OUTCOMING_MAGIC_DAMAGE_MODIFIER =  [1.07, 1.12, 1.17, 1.2, 1.25]
    OUTCOMING_PHYSIC_DAMAGE_MODIFIER = [1.07, 1.12, 1.17, 1.2, 1.25]

    INCOMING_MAGIC_DAMAGE_MODIFIER =  [1.025, 1.04, 1.07, 1.1, 1.125]
    INCOMING_PHYSIC_DAMAGE_MODIFIER = [1.025, 1.04, 1.07, 1.1, 1.125]


ABILITIES = dict( (ability.get_id(), ability)
                  for ability in globals().values()
                  if isinstance(ability, type) and issubclass(ability, AbilityModifiersBase) and ability != AbilityModifiersBase)
