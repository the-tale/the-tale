
import smart_imports

smart_imports.all()


class _CompanionAbilityModifier(prototypes.AbilityPrototype):
    TYPE = relations.ABILITY_TYPE.COMPANION
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = relations.ABILITY_AVAILABILITY.FOR_PLAYERS

    EFFECT_TYPE = None

    def modify_attribute(self, type_, value):
        if type_.is_COMPANION_ABILITIES_LEVELS:
            value[self.EFFECT_TYPE] = self.level
        return value


class WALKER(_CompanionAbilityModifier):
    NAME = 'Ходок'
    normalized_name = NAME
    DESCRIPTION = 'Ходоки знают как лучше использовать дорожные особенности спутников.'
    EFFECT_TYPE = companions_abilities_relations.METATYPE.TRAVEL


class COMRADE(_CompanionAbilityModifier):
    NAME = 'Боевой товарищ'
    normalized_name = NAME
    DESCRIPTION = 'Герой обращается со спутником как с боевым товарищем, благодаря чему улучшаются все боевые особенности спутника.'
    EFFECT_TYPE = companions_abilities_relations.METATYPE.BATTLE


class ECONOMIC(_CompanionAbilityModifier):
    NAME = 'Бухгалтер'
    normalized_name = NAME
    DESCRIPTION = 'Герои с бухгалтерской жилкой ответственно подходят не только к своему имуществу, но и к имуществу спутника. Способность улучшает денежные особенности спутника.'
    EFFECT_TYPE = companions_abilities_relations.METATYPE.MONEY


class IMPROVISER(_CompanionAbilityModifier):
    NAME = 'Импровизатор'
    normalized_name = NAME
    DESCRIPTION = 'Герой всегда готов помочь своему спутнику в любых его делах, что усиливает его необычные особенности.'
    EFFECT_TYPE = companions_abilities_relations.METATYPE.OTHER


class THOUGHTFUL(prototypes.AbilityPrototype):

    TYPE = relations.ABILITY_TYPE.COMPANION
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = relations.ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = 'Заботливый'
    normalized_name = NAME
    DESCRIPTION = 'Окружённый заботой героя, спутник увеличивает своё максимальное здоровье.'

    MULTIPLIER = [1.1, 1.2, 1.3, 1.4, 1.5]

    @property
    def multiplier(self): return self.MULTIPLIER[self.level - 1]

    def modify_attribute(self, type_, value): return value * self.multiplier if type_.is_COMPANION_MAX_HEALTH else value


class COHERENCE(prototypes.AbilityPrototype):

    TYPE = relations.ABILITY_TYPE.COMPANION
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = relations.ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = 'Товарищ'
    normalized_name = NAME
    DESCRIPTION = 'Путешествия со спутником сложны и требуют от героя особых навыков. Умение по-товарищески относиться к спутнику определяет максимальную слаженность спутника. Она увеличивается на 20 за уровень способности. При сбросе навыка заработанная слаженность не теряется, но ограничивается его актуальным значением.'

    COHERENCE = [20, 40, 60, 80, 100]

    @property
    def coherence(self): return self.COHERENCE[self.level - 1]

    def modify_attribute(self, type_, value): return value + self.coherence if type_.is_COMPANION_MAX_COHERENCE else value


class _CompanionHealBase(prototypes.AbilityPrototype):
    TYPE = relations.ABILITY_TYPE.COMPANION
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = relations.ABILITY_AVAILABILITY.FOR_PLAYERS

    PROBABILITY = [c.COMPANIONS_HERO_REGEN_ON_HEAL_PER_HEAL * 0.2,
                   c.COMPANIONS_HERO_REGEN_ON_HEAL_PER_HEAL * 0.4,
                   c.COMPANIONS_HERO_REGEN_ON_HEAL_PER_HEAL * 0.6,
                   c.COMPANIONS_HERO_REGEN_ON_HEAL_PER_HEAL * 0.8,
                   c.COMPANIONS_HERO_REGEN_ON_HEAL_PER_HEAL * 1.0]
    MODIFIER = None

    @property
    def probability(self): return self.PROBABILITY[self.level - 1]

    def modify_attribute(self, type_, value):
        if type_ == self.MODIFIER:
            value += self.probability
        return value


def get_being_types(modifier):
    return [t.text for t in tt_beings_relations.TYPE.records if modifier in (t.companion_heal_modifier, t.companion_coherence_modifier)]


class HEALING(_CompanionHealBase):
    NAME = 'Врачевание'
    normalized_name = NAME
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_LIVING_HEAL
    BEING_TYPES = get_being_types(MODIFIER)
    DESCRIPTION = 'Умение обращаться с ниткой, иголкой и хирургическим ножом позволяет иногда восстановить немного здоровья живому (%s) спутнику.' % ', '.join(BEING_TYPES)


class MAGE_MECHANICS(_CompanionHealBase):
    NAME = 'Магомеханика'
    normalized_name = NAME
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_CONSTRUCT_HEAL
    BEING_TYPES = get_being_types(MODIFIER)
    DESCRIPTION = 'С помощью плоскогубцев, проволоки и толики магии магомеханик иногда может отремонтировать своего магомеханического (%s) спутника.' % ', '.join(BEING_TYPES)


class WITCHCRAFT(_CompanionHealBase):
    NAME = 'Ведовство'
    normalized_name = NAME
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_UNUSUAL_HEAL
    BEING_TYPES = get_being_types(MODIFIER)
    DESCRIPTION = 'Герой, сведущий в нетрадиционных областях знаний, иногда может восстановить здоровье особого (%s) спутника.' % ', '.join(BEING_TYPES)


class _CompanionCoherenceSpeedBase(prototypes.AbilityPrototype):
    TYPE = relations.ABILITY_TYPE.COMPANION
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = relations.ABILITY_AVAILABILITY.FOR_PLAYERS

    SPEED = [1.2, 1.4, 1.6, 1.8, 2.0]
    MODIFIER = None

    @property
    def speed(self): return self.SPEED[self.level - 1]

    def modify_attribute(self, type_, value):
        if type_ == self.MODIFIER:
            value *= self.speed
        return value


class SOCIABILITY(_CompanionCoherenceSpeedBase):
    NAME = 'Коммуникабельность'
    normalized_name = NAME
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_LIVING_COHERENCE_SPEED
    BEING_TYPES = get_being_types(MODIFIER)
    DESCRIPTION = 'Хороший разговор сближает лучше кровавой стычки, коммуникабельный герой быстрее увеличивает слаженность живого (%s) спутника.' % ', '.join(BEING_TYPES)


class SERVICE(_CompanionCoherenceSpeedBase):
    NAME = 'Обслуживание'
    normalized_name = NAME
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_CONSTRUCT_COHERENCE_SPEED
    BEING_TYPES = get_being_types(MODIFIER)
    DESCRIPTION = 'Каждому магомеханическому (%s) спутнику требуется регулярная смазка, или подзарядка кристаллов, или ещё какая-нибудь заумная операция. Чем ответственнее герой относится к обслуживанию своего спутника, тем быстрее растёт его слаженность.' % ', '.join(BEING_TYPES)


class SACREDNESS(_CompanionCoherenceSpeedBase):
    NAME = 'Сакральность'
    normalized_name = NAME
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_UNUSUAL_COHERENCE_SPEED
    BEING_TYPES = get_being_types(MODIFIER)
    DESCRIPTION = 'Особые (%s) спутники настолько необычны, что герою приходится учиться думать как его напарник. Если герою удаётся найти схожие струны в душе спутника, то их слаженность начинает расти быстрее.' % ', '.join(BEING_TYPES)


ABILITIES = dict((ability.get_id(), ability)
                 for ability in globals().values()
                 if (isinstance(ability, type) and
                     issubclass(ability, prototypes.AbilityPrototype) and
                     ability != prototypes.AbilityPrototype and not ability.__name__.startswith('_')))
