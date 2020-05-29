
import smart_imports

smart_imports.all()


class RatingValuesPrototype(utils_prototypes.BasePrototype):
    _model_class = models.RatingValues
    _readonly = ('id', 'account_id', 'might', 'bills_count', 'magic_power', 'physic_power', 'level',
                 'phrases_count', 'pvp_battles_1x1_number', 'pvp_battles_1x1_victories', 'referrals_number',
                 'achievements_points', 'help_count', 'gifts_returned', 'politics_power')
    _bidirectional = ()
    _get_by = ('account_id', )

    @utils_decorators.lazy_property
    def account(self): return accounts_prototypes.AccountPrototype(self._model.account)

    @classmethod
    @django_transaction.atomic
    def recalculate(cls):

        models.RatingValues.objects.all().delete()

        cursor = django_db.connection.cursor()

        sql_request = '''
INSERT INTO %(ratings)s (account_id, might, bills_count, magic_power, physic_power, level, phrases_count, pvp_battles_1x1_number, pvp_battles_1x1_victories, referrals_number, achievements_points, help_count, gifts_returned, politics_power)
SELECT %(accounts)s.id AS account_id,
       %(heroes)s.might AS might,
       CASE WHEN raw_bills_count IS NULL THEN 0 ELSE raw_bills_count END AS bills_count,
       %(heroes)s.raw_power_magic AS magic_power,
       %(heroes)s.raw_power_physic AS physic_power,
       %(heroes)s.level AS level,
       CASE WHEN raw_phrases_count IS NULL THEN 0 ELSE raw_phrases_count END AS phrases_count,
       %(heroes)s.stat_pvp_battles_1x1_number AS pvp_battles_1x1_number,
       CASE WHEN %(heroes)s.stat_pvp_battles_1x1_number < %(min_pvp_battles)s THEN 0 ELSE CAST(%(heroes)s.stat_pvp_battles_1x1_victories AS FLOAT) / %(heroes)s.stat_pvp_battles_1x1_number END AS pvp_battles_1x1_victories,
       %(accounts)s.referrals_number as referrals_number,
       %(achievements)s.points as achievements_points,
       %(heroes)s.stat_help_count as help_count,
       %(heroes)s.stat_gifts_returned as gifts_returned,
       %(heroes)s.stat_politics_multiplier as politics_power
FROM %(accounts)s
JOIN %(heroes)s ON %(accounts)s.id=%(heroes)s.account_id
JOIN %(achievements)s ON %(accounts)s.id=%(achievements)s.account_id
LEFT OUTER JOIN ( SELECT %(bills)s.owner_id AS bills_owner_id, COUNT(%(bills)s.owner_id) AS raw_bills_count
                  FROM %(bills)s
                  WHERE %(bills)s.state=%(bill_accepted_state)s GROUP BY %(bills)s.owner_id ) AS bills_subquery
           ON %(accounts)s.id=bills_owner_id
LEFT OUTER JOIN ( SELECT %(phrase_candidates)s.account_id AS phrase_author_id, COUNT(%(phrase_candidates)s.account_id) AS raw_phrases_count
                  FROM %(phrase_candidates)s
                  WHERE %(phrase_candidates)s.type=%(phrase_candidate_type)s GROUP BY %(phrase_candidates)s.account_id ) AS phrases_subquery
           ON %(accounts)s.id=phrase_author_id
WHERE %(accounts)s.removed_at IS NULL AND NOT %(accounts)s.is_fast AND NOT %(accounts)s.is_bot AND %(accounts)s.id <> %(system_user_id)s AND %(accounts)s.ban_game_end_at < current_timestamp
'''

        sql_request = sql_request % {'ratings': models.RatingValues._meta.db_table,
                                     'accounts': accounts_models.Account._meta.db_table,
                                     'achievements': achievements_models.AccountAchievements._meta.db_table,
                                     'heroes': heroes_models.Hero._meta.db_table,
                                     'bills': bills_models.Bill._meta.db_table,
                                     'bill_accepted_state': bills_relations.BILL_STATE.ACCEPTED.value,
                                     'phrase_candidates': linguistics_prototypes.ContributionPrototype._model_class._meta.db_table,
                                     'phrase_candidate_type': linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE.value,
                                     'min_pvp_battles': heroes_conf.settings.MIN_PVP_BATTLES,
                                     'system_user_id': accounts_logic.get_system_user().id}

        cursor.execute(sql_request)


class RatingPlacesPrototype(utils_prototypes.BasePrototype):
    _model_class = models.RatingPlaces
    _readonly = ('id', 'account_id', 'might_place', 'bills_count_place', 'magic_power_place', 'physic_power_place', 'level_place',
                 'phrases_count_place', 'pvp_battles_1x1_number_place', 'pvp_battles_1x1_victories_place', 'referrals_number_place',
                 'achievements_points_place', 'help_count_place', 'gifts_returned_place', 'politics_power_place')
    _bidirectional = ()
    _get_by = ('account_id', )

    @utils_decorators.lazy_property
    def account(self): return accounts_prototypes.AccountPrototype(self._model.account)

    @classmethod
    @django_transaction.atomic
    def recalculate(cls):

        models.RatingPlaces.objects.all().delete()

        cursor = django_db.connection.cursor()

        sql_request = '''
INSERT INTO %(places)s (account_id, might_place, bills_count_place, magic_power_place, physic_power_place, level_place, phrases_count_place, pvp_battles_1x1_number_place, pvp_battles_1x1_victories_place, referrals_number_place, achievements_points_place, help_count_place, gifts_returned_place, politics_power_place)
SELECT might_table.account_id AS account_id,
       might_table.might_place AS might_place,
       bills_count_table.bills_count_place AS bills_count_place,
       magic_power_table.magic_power_place AS magic_power_place,
       physic_power_table.physic_power_place AS physic_power_place,
       level_table.level_place AS level_place,
       phrases_count_table.phrases_count_place AS phrases_count_place,
       pvp_battles_1x1_number_table.pvp_battles_1x1_number_place AS pvp_battles_1x1_number_place,
       pvp_battles_1x1_victories_table.pvp_battles_1x1_victories_place AS pvp_battles_1x1_victories_place,
       referrals_number_table.referrals_number_place AS referrals_number_place,
       achievements_points_place_table.achievements_points_place AS achievements_points_place,
       help_count_table.help_count_place AS help_count_place,
       gifts_returned_table.gifts_returned_place AS gifts_returned_place,
       politics_power_table.politics_power_place AS politics_power_place
FROM (SELECT %(ratings)s.account_id AS account_id, row_number() OVER (ORDER BY %(ratings)s.might DESC, %(ratings)s.account_id) AS might_place FROM %(ratings)s) as might_table
JOIN (SELECT %(ratings)s.account_id AS account_id, row_number() OVER (ORDER BY %(ratings)s.bills_count DESC, %(ratings)s.account_id) AS bills_count_place FROM %(ratings)s) as bills_count_table
    ON might_table.account_id=bills_count_table.account_id
JOIN (SELECT %(ratings)s.account_id AS account_id, row_number() OVER (ORDER BY %(ratings)s.level DESC, %(ratings)s.account_id) AS level_place FROM %(ratings)s) as level_table
    ON might_table.account_id=level_table.account_id
JOIN (SELECT %(ratings)s.account_id AS account_id, row_number() OVER (ORDER BY %(ratings)s.magic_power DESC, %(ratings)s.account_id) AS magic_power_place FROM %(ratings)s) as magic_power_table
    ON might_table.account_id=magic_power_table.account_id
JOIN (SELECT %(ratings)s.account_id AS account_id, row_number() OVER (ORDER BY %(ratings)s.physic_power DESC, %(ratings)s.account_id) AS physic_power_place FROM %(ratings)s) as physic_power_table
    ON might_table.account_id=physic_power_table.account_id
JOIN (SELECT %(ratings)s.account_id AS account_id, row_number() OVER (ORDER BY %(ratings)s.phrases_count DESC, %(ratings)s.account_id) AS phrases_count_place FROM %(ratings)s) as phrases_count_table
    ON might_table.account_id=phrases_count_table.account_id
JOIN (SELECT %(ratings)s.account_id AS account_id, row_number() OVER (ORDER BY %(ratings)s.pvp_battles_1x1_number DESC, %(ratings)s.account_id) AS pvp_battles_1x1_number_place FROM %(ratings)s) as pvp_battles_1x1_number_table
    ON might_table.account_id=pvp_battles_1x1_number_table.account_id
JOIN (SELECT %(ratings)s.account_id AS account_id, row_number() OVER (ORDER BY %(ratings)s.pvp_battles_1x1_victories DESC, %(ratings)s.account_id) AS pvp_battles_1x1_victories_place FROM %(ratings)s) as pvp_battles_1x1_victories_table
    ON might_table.account_id=pvp_battles_1x1_victories_table.account_id
JOIN (SELECT %(ratings)s.account_id AS account_id, row_number() OVER (ORDER BY %(ratings)s.referrals_number DESC, %(ratings)s.account_id) AS referrals_number_place FROM %(ratings)s) as referrals_number_table
    ON might_table.account_id=referrals_number_table.account_id
JOIN (SELECT %(ratings)s.account_id AS account_id, row_number() OVER (ORDER BY %(ratings)s.achievements_points DESC, %(ratings)s.account_id) AS achievements_points_place FROM %(ratings)s) as achievements_points_place_table
    ON might_table.account_id=achievements_points_place_table.account_id
JOIN (SELECT %(ratings)s.account_id AS account_id, row_number() OVER (ORDER BY %(ratings)s.help_count DESC, %(ratings)s.account_id) AS help_count_place FROM %(ratings)s) as help_count_table
    ON might_table.account_id=help_count_table.account_id
JOIN (SELECT %(ratings)s.account_id AS account_id, row_number() OVER (ORDER BY %(ratings)s.gifts_returned DESC, %(ratings)s.account_id) AS gifts_returned_place FROM %(ratings)s) as gifts_returned_table
    ON might_table.account_id=gifts_returned_table.account_id
JOIN (SELECT %(ratings)s.account_id AS account_id, row_number() OVER (ORDER BY %(ratings)s.politics_power DESC, %(ratings)s.account_id) AS politics_power_place FROM %(ratings)s) as politics_power_table
    ON might_table.account_id=politics_power_table.account_id
'''

        sql_request = sql_request % {'places': models.RatingPlaces._meta.db_table,
                                     'ratings': models.RatingValues._meta.db_table,
                                     'accounts': accounts_models.Account._meta.db_table}

        cursor.execute(sql_request)

        global_settings[conf.settings.SETTINGS_UPDATE_TIMESTEMP_KEY] = str(time.time())
