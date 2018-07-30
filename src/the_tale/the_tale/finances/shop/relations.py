
import smart_imports

smart_imports.all()


INFINIT_PREMIUM_DESCRIPTION = 'Вечная подписка даёт вам все бонусы подписчика на всё время игры.'


class PERMANENT_PURCHASE_TYPE(rels_django.DjangoEnum):
    description = rels.Column(unique=False)
    might_required = rels.Column(unique=False, single_type=False)
    level_required = rels.Column(unique=False, single_type=False)
    full_name = rels.Column()

    records = (('INFINIT_SUBSCRIPTION', 12, 'Вечная подписка', INFINIT_PREMIUM_DESCRIPTION, None, None, 'Вечная подписка'),)


class GOODS_GROUP(rels_django.DjangoEnum):
    uid = rels.Column()
    uid_prefix = rels.Column(unique=False)

    records = (('PREMIUM', 0, 'подписка', 'subscription', 'subscription-'),
               ('ENERGY', 1, 'энергия', 'energy', 'energy-'),
               ('CHEST', 2, 'сундук', 'random-premium-chest', 'random-premium-chest'),
               ('PREFERENCES', 3, 'предпочтения', 'preference', 'preference-'),
               ('PREFERENCES_RESET', 4, 'сброс предпочтений', 'preference-reset', 'hero-preference-reset-'),
               ('HABITS', 5, 'черты', 'habits', 'hero-habits-'),
               ('ABILITIES', 6, 'способности', 'abilities', 'hero-abilities-'),
               ('CLANS', 7, 'гильдии', 'clans', 'clan-'),
               ('CARDS', 8, 'Карты судьбы', 'cards', 'cards-'))


CARDS_MIN_PRICES = {cards_relations.RARITY.COMMON: 2,
                    cards_relations.RARITY.UNCOMMON: 10,
                    cards_relations.RARITY.RARE: 25,
                    cards_relations.RARITY.EPIC: 50,
                    cards_relations.RARITY.LEGENDARY: 100}
