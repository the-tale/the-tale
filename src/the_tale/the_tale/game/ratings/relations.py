
import smart_imports

smart_imports.all()


class RATING_TYPE(rels_django.DjangoEnum):
    hint = rels.Column(primary=False, unique=False)
    field = rels.Column()

    records = (('MIGHT', 'might', 'Могущество', '', 'might'),
               ('BILLS', 'bills', 'Принятые записи в Книге Судеб', '', 'bills_count'),
               ('MAGIC_POWER', 'magic-power', 'Магическая сила героя', '', 'magic_power'),
               ('PHYSIC_POWER', 'physic-power', 'Физическая сила героя', '', 'physic_power'),
               ('LEVEL', 'level', 'Уровень героя', '', 'level'),
               ('PHRASES', 'phrases', 'Добавленные фразы', '', 'phrases_count'),
               ('PVP_BATTLES_1x1_NUMBER', 'pvp_battles_1x1_number', 'Сражения в PvP', '', 'pvp_battles_1x1_number'),
               ('PVP_BATTLES_1x1_VICTORIES', 'pvp_battles_1x1_victories', 'Победы в PvP',
                'Для участия в рейтинге необходимо провести минимум %(min_pvp_battles)s боёв' % {'min_pvp_battles': heroes_conf.settings.MIN_PVP_BATTLES}, 'pvp_battles_1x1_victories'),
               ('REFERRALS_NUMBER', 'referrals_number', 'Последователи', '', 'referrals_number'),
               ('ACHIEVEMENTS_POINTS', 'achievements_points', 'Очки достижений', '', 'achievements_points'),
               ('POLITICS_POWER', 'politics_power', 'Влиятельность', 'Влияние, которое герой оказывает своими заданиями (участвуют только герои, влияющие на всех Мастеров)', 'politics_power'),
               )
