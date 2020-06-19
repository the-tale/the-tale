
import smart_imports

smart_imports.all()


class Hero(django_models.Model):

    MAX_NAME_LENGTH = 32

    created_at_turn = django_models.IntegerField(null=False, default=0)
    saved_at_turn = django_models.IntegerField(null=False, default=0)
    last_rare_operation_at_turn = django_models.IntegerField(null=False, default=0)

    saved_at = django_models.DateTimeField(auto_now=True)

    account = django_models.ForeignKey('accounts.Account', related_name='heroes', default=None, null=True, blank=True, on_delete=django_models.CASCADE)

    clan = django_models.ForeignKey('clans.Clan', related_name='+', default=None, null=True, blank=True, on_delete=django_models.PROTECT)

    is_fast = django_models.BooleanField(default=True, db_index=True)  # copy from account.is_fast
    is_bot = django_models.BooleanField(default=False)

    is_alive = django_models.BooleanField(default=True)

    active_state_end_at = django_models.DateTimeField(db_index=True, default=datetime.datetime.fromtimestamp(0))
    premium_state_end_at = django_models.DateTimeField(db_index=True, default=datetime.datetime.fromtimestamp(0))
    ban_state_end_at = django_models.DateTimeField(db_index=True, default=datetime.datetime.fromtimestamp(0))

    # time when ui caching and model saving has started
    ui_caching_started_at = django_models.DateTimeField(auto_now_add=True)

    # base
    gender = rels_django.RelationIntegerField(relation=game_relations.GENDER, relation_column='value')
    race = rels_django.RelationIntegerField(relation=game_relations.RACE, relation_column='value')

    level = django_models.IntegerField(null=False, default=1)
    experience = django_models.IntegerField(null=False, default=0)

    health = django_models.IntegerField(null=False, default=0.0)

    raw_power_magic = django_models.BigIntegerField(null=False, default=0)  # special field for ratings
    raw_power_physic = django_models.BigIntegerField(null=False, default=0)  # special field for ratings

    money = django_models.BigIntegerField(null=False, default=0)

    data = django_postgres_fields.JSONField()

    actions = django_models.TextField()

    quest_created_time = django_models.DateTimeField(db_index=True, default=datetime.datetime.fromtimestamp(0))

    next_spending = rels_django.RelationIntegerField(relation=relations.ITEMS_OF_EXPENDITURE, relation_column='value')

    might = django_models.FloatField(null=False, default=0.0)

    preferences = django_models.TextField()

    habit_honor = django_models.FloatField(default=0)
    habit_peacefulness = django_models.FloatField(default=0)

    # statistics
    stat_pve_deaths = django_models.BigIntegerField(default=0, null=False)
    stat_pve_kills = django_models.BigIntegerField(default=0, null=False)

    stat_money_earned_from_loot = django_models.BigIntegerField(default=0, null=False)
    stat_money_earned_from_artifacts = django_models.BigIntegerField(default=0, null=False)
    stat_money_earned_from_quests = django_models.BigIntegerField(default=0, null=False)
    stat_money_earned_from_help = django_models.BigIntegerField(default=0, null=False)
    stat_money_earned_from_habits = django_models.BigIntegerField(default=0, null=False)
    stat_money_earned_from_companions = django_models.BigIntegerField(default=0, null=False)
    stat_money_earned_from_masters = django_models.BigIntegerField(default=0, null=False)

    stat_money_spend_for_heal = django_models.BigIntegerField(default=0, null=False)
    stat_money_spend_for_artifacts = django_models.BigIntegerField(default=0, null=False)
    stat_money_spend_for_sharpening = django_models.BigIntegerField(default=0, null=False)
    stat_money_spend_for_useless = django_models.BigIntegerField(default=0, null=False)
    stat_money_spend_for_impact = django_models.BigIntegerField(default=0, null=False)
    stat_money_spend_for_experience = django_models.BigIntegerField(default=0, null=False)
    stat_money_spend_for_repairing = django_models.BigIntegerField(default=0, null=False)
    stat_money_spend_for_tax = django_models.BigIntegerField(default=0, null=False)
    stat_money_spend_for_companions = django_models.BigIntegerField(default=0, null=False)

    stat_artifacts_had = django_models.BigIntegerField(default=0, null=False)
    stat_loot_had = django_models.BigIntegerField(default=0, null=False)

    stat_quests_done = django_models.BigIntegerField(default=0, null=False)

    stat_companions_count = django_models.BigIntegerField(default=0, null=False)

    stat_pvp_battles_1x1_number = django_models.BigIntegerField(default=0, null=False)
    stat_pvp_battles_1x1_victories = django_models.BigIntegerField(default=0, null=False)
    stat_pvp_battles_1x1_draws = django_models.BigIntegerField(default=0, null=False)

    stat_cards_used = django_models.BigIntegerField(default=0, null=False)
    stat_cards_combined = django_models.BigIntegerField(default=0, null=False)

    stat_politics_multiplier = django_models.FloatField(default=0, null=False)  # for ratings

    def __str__(self):
        return 'hero[%s] — %s' % (self.id, self.data['name']['forms'][0])


# just copy for collection statistics
class HeroPreferences(django_models.Model):

    hero = django_models.ForeignKey(Hero, on_delete=django_models.CASCADE)

    religion_type = rels_django.RelationIntegerField(null=False, relation=relations.RELIGION_TYPE)
    mob = django_models.ForeignKey('mobs.MobRecord', null=True, default=None, blank=True, on_delete=django_models.PROTECT)
    place = django_models.ForeignKey('places.Place', null=True, default=None, related_name='+', blank=True, on_delete=django_models.PROTECT)
    friend = django_models.ForeignKey('persons.Person', null=True, default=None, related_name='+', blank=True, on_delete=django_models.PROTECT)
    enemy = django_models.ForeignKey('persons.Person', null=True, default=None, related_name='+', blank=True, on_delete=django_models.PROTECT)
    equipment_slot = rels_django.RelationIntegerField(relation=relations.EQUIPMENT_SLOT, null=True, default=None, blank=True)
    risk_level = rels_django.RelationIntegerField(relation=relations.RISK_LEVEL)
    favorite_item = rels_django.RelationIntegerField(relation=relations.EQUIPMENT_SLOT, null=True, default=None, blank=True)
    archetype = rels_django.RelationIntegerField(relation=game_relations.ARCHETYPE, null=True, default=None, blank=True)
    companion_dedication = rels_django.RelationIntegerField(relation=relations.COMPANION_DEDICATION, null=True, default=None, blank=True)
    companion_empathy = rels_django.RelationIntegerField(relation=relations.COMPANION_EMPATHY, null=True, default=None, blank=True)
    quests_region = django_models.ForeignKey('places.Place', null=True, default=None, related_name='+', blank=True, on_delete=django_models.PROTECT)
    quests_region_size = django_models.IntegerField(default=c.DEFAULT_QUESTS_REGION_SIZE)

    @classmethod
    def create(cls, hero, religion_type, risk_level, archetype, companion_dedication, companion_empathy):
        return cls.objects.create(hero_id=hero.id,
                                  religion_type=religion_type,
                                  risk_level=risk_level,
                                  archetype=archetype,
                                  companion_dedication=companion_dedication,
                                  companion_empathy=companion_empathy)

    @classmethod
    def update(cls, hero_id, field, value):
        cls.objects.filter(hero_id=hero_id).update(**{field: value})


class HeroDescription(django_models.Model):

    hero = django_models.OneToOneField(Hero, on_delete=django_models.CASCADE)

    text = django_models.TextField(null=False, default='', blank=True)
