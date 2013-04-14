# coding: utf-8
import time

from dext.utils.decorators import nested_commit_on_success
from dext.settings import settings

from common.utils.decorators import lazy_property
from common.utils.prototypes import BasePrototype

from accounts.models import Account
from accounts.prototypes import AccountPrototype

from game.heroes.models import Hero
from game.bills.models import Bill, BILL_STATE
from game.phrase_candidates.models import PhraseCandidate, PHRASE_CANDIDATE_STATE

from game.ratings.models import RatingValues, RatingPlaces
from game.ratings.conf import ratings_settings


class RatingValuesPrototype(BasePrototype):
    _model_class = RatingValues
    _readonly = ('id', 'account_id', 'might', 'bills_count', 'power', 'level', 'phrases_count', 'pvp_battles_1x1_number', 'pvp_battles_1x1_victories')
    _bidirectional = ()
    _get_by = ('account_id', )

    @lazy_property
    def account(self): return AccountPrototype(self._model.account)

    @classmethod
    @nested_commit_on_success
    def recalculate(cls):
        from django.db import connection, transaction

        RatingValues.objects.all().delete()


        cursor = connection.cursor()


        sql_request = '''
INSERT INTO %(ratings)s (account_id, might, bills_count, power, level, phrases_count, pvp_battles_1x1_number, pvp_battles_1x1_victories)
SELECT %(accounts)s.id AS account_id,
       %(heroes)s.might AS might,
       CASE WHEN raw_bills_count IS NULL THEN 0 ELSE raw_bills_count END AS bills_count,
       %(heroes)s.raw_power AS power,
       %(heroes)s.level AS level,
       CASE WHEN raw_phrases_count IS NULL THEN 0 ELSE raw_phrases_count END AS phrases_count,
       %(heroes)s.stat_pvp_battles_1x1_number AS pvp_battles_1x1_number,
       CASE WHEN %(heroes)s.stat_pvp_battles_1x1_number=0 THEN 0 ELSE CAST(%(heroes)s.stat_pvp_battles_1x1_victories AS FLOAT) / %(heroes)s.stat_pvp_battles_1x1_number END AS pvp_battles_1x1_victories
FROM %(accounts)s
JOIN %(heroes)s ON %(accounts)s.id=%(heroes)s.account_id
LEFT OUTER JOIN ( SELECT %(bills)s.owner_id AS bills_owner_id, COUNT(%(bills)s.owner_id) AS raw_bills_count
                  FROM %(bills)s
                  WHERE %(bills)s.state=%(bill_accepted_state)s GROUP BY %(bills)s.owner_id ) AS bills_subquery
           ON %(accounts)s.id=bills_owner_id
LEFT OUTER JOIN ( SELECT %(phrase_candidates)s.author_id AS phrase_author_id, COUNT(%(phrase_candidates)s.author_id) AS raw_phrases_count
                  FROM %(phrase_candidates)s
                  WHERE %(phrase_candidates)s.state=%(phrase_candidate_added_state)s GROUP BY %(phrase_candidates)s.author_id ) AS phrases_subquery
           ON %(accounts)s.id=phrase_author_id
WHERE NOT %(accounts)s.is_fast
'''

        sql_request = sql_request % {'ratings': RatingValues._meta.db_table,
                                     'accounts': Account._meta.db_table,
                                     'heroes': Hero._meta.db_table,
                                     'bills': Bill._meta.db_table,
                                     'bill_accepted_state': BILL_STATE.ACCEPTED.value,
                                     'phrase_candidates': PhraseCandidate._meta.db_table,
                                     'phrase_candidate_added_state': PHRASE_CANDIDATE_STATE.ADDED }

        cursor.execute(sql_request)

        transaction.commit_unless_managed()




class RatingPlacesPrototype(BasePrototype):
    _model_class = RatingPlaces
    _readonly = ('id', 'account_id', 'might_place', 'bills_count_place', 'power_place',
                 'level_place', 'phrases_count_place', 'pvp_battles_1x1_number_place', 'pvp_battles_1x1_victories_place')
    _bidirectional = ()
    _get_by = ('account_id', )

    @lazy_property
    def account(self): return AccountPrototype(self._model.account)

    @classmethod
    @nested_commit_on_success
    def recalculate(cls):
        from django.db import connection, transaction

        RatingPlaces.objects.all().delete()

        cursor = connection.cursor()

        sql_request = '''
INSERT INTO %(places)s (account_id, might_place, bills_count_place, power_place, level_place, phrases_count_place, pvp_battles_1x1_number_place, pvp_battles_1x1_victories_place)
SELECT might_table.account_id AS account_id,
       might_table.might_place AS might_place,
       bills_count_table.bills_count_place AS bills_count_place,
       power_table.power_place AS power_place,
       level_table.level_place AS level_place,
       phrases_count_table.phrases_count_place AS phrases_count_place,
       pvp_battles_1x1_number_table.pvp_battles_1x1_number_place AS pvp_battles_1x1_number_place,
       pvp_battles_1x1_victories_table.pvp_battles_1x1_victories_place AS pvp_battles_1x1_victories_place
FROM (SELECT %(ratings)s.account_id AS account_id, row_number() OVER (ORDER BY %(ratings)s.might DESC, %(ratings)s.account_id) AS might_place FROM %(ratings)s) as might_table
JOIN (SELECT %(ratings)s.account_id AS account_id, row_number() OVER (ORDER BY %(ratings)s.bills_count DESC, %(ratings)s.account_id) AS bills_count_place FROM %(ratings)s) as bills_count_table
    ON might_table.account_id=bills_count_table.account_id
JOIN (SELECT %(ratings)s.account_id AS account_id, row_number() OVER (ORDER BY %(ratings)s.level DESC, %(ratings)s.account_id) AS level_place FROM %(ratings)s) as level_table
    ON might_table.account_id=level_table.account_id
JOIN (SELECT %(ratings)s.account_id AS account_id, row_number() OVER (ORDER BY %(ratings)s.power DESC, %(ratings)s.account_id) AS power_place FROM %(ratings)s) as power_table
    ON might_table.account_id=power_table.account_id
JOIN (SELECT %(ratings)s.account_id AS account_id, row_number() OVER (ORDER BY %(ratings)s.phrases_count DESC, %(ratings)s.account_id) AS phrases_count_place FROM %(ratings)s) as phrases_count_table
    ON might_table.account_id=phrases_count_table.account_id
JOIN (SELECT %(ratings)s.account_id AS account_id, row_number() OVER (ORDER BY %(ratings)s.pvp_battles_1x1_number DESC, %(ratings)s.account_id) AS pvp_battles_1x1_number_place FROM %(ratings)s) as pvp_battles_1x1_number_table
    ON might_table.account_id=pvp_battles_1x1_number_table.account_id
JOIN (SELECT %(ratings)s.account_id AS account_id, row_number() OVER (ORDER BY %(ratings)s.pvp_battles_1x1_victories DESC, %(ratings)s.account_id) AS pvp_battles_1x1_victories_place FROM %(ratings)s) as pvp_battles_1x1_victories_table
    ON might_table.account_id=pvp_battles_1x1_victories_table.account_id
'''

        sql_request = sql_request % {'places': RatingPlaces._meta.db_table,
                                     'ratings': RatingValues._meta.db_table,
                                     'accounts': Account._meta.db_table}

        cursor.execute(sql_request)

        transaction.commit_unless_managed()

        settings[ratings_settings.SETTINGS_UPDATE_TIMESTEMP_KEY] = str(time.time())
