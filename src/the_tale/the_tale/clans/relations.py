
import smart_imports

smart_imports.all()


class STATE(rels_django.DjangoEnum):
    records = (('ACTIVE', 0, 'активна'),
               ('REMOVED', 1, 'удалена'),)


class ORDER_BY(rels_django.DjangoEnum):
    order_field = rels.Column()

    records = (('NAME_DESC', 0, 'имени▲', ('-name',)),
               ('NAME_ASC', 1, 'имени▼', ('name',)),
               ('ABBR_DESC', 2, 'аббревиатуре▲', ('-abbr', 'name')),
               ('ABBR_ASC', 3, 'аббревиатуре▼', ('abbr', 'name')),
               ('MEMBERS_NUMBER_DESC', 4, 'количеству Хранителей▲', ('-members_number', 'name')),
               ('MEMBERS_NUMBER_ASC', 5, 'количеству Хранителей▼', ('members_number', 'name')),
               ('ACTIVE_MEMBERS_NUMBER_DESC', 6, 'количеству активных Хранителей▲', ('-active_members_number', 'name')),
               ('ACTIVE_MEMBERS_NUMBER_ASC', 7, 'количеству активных Хранителей▼', ('active_members_number', 'name')),
               ('PREMIUM_MEMBERS_NUMBER_DESC', 8, 'количеству подписчиков▲', ('-premium_members_number', 'name')),
               ('PREMIUM_MEMBERS_NUMBER_ASC', 9, 'количеству подписчиков▼', ('premium_members_number', 'name')),
               ('MIGHT_DESC', 10, 'могуществу▲', ('-might', 'name')),
               ('MIGHT_ASC', 11, 'могуществу▼', ('might', 'name')),
               ('CREATED_AT_DESC', 12, 'дате создания▲', ('-created_at', 'name')),
               ('CREATED_AT_ASC', 13, 'дате создания▼', ('created_at', 'name')))


class MEMBERSHIP_REQUEST_TYPE(rels_django.DjangoEnum):
    records = (('FROM_CLAN', 0, 'от гильдии'),
               ('FROM_ACCOUNT', 1, 'от аккаунта'))


class PAGE_ID(rels_django.DjangoEnum):
    records = (('INDEX', 0, 'индексная страница'),
               ('NEW', 1, 'создание гильдии'),
               ('SHOW', 2, 'страница гильдии'),
               ('EDIT', 3, 'редактирование гильдии'),
               ('FOR_CLAN', 4, 'заявки в гильдию'),
               ('FOR_ACCOUNT', 5, 'предложения вступить в гильдию'),
               ('CHRONICLE', 6, 'хроника гильдии'),
               ('EDIT_MEMBER', 7, 'редактирование члена гильдии'))


def meta_object_receiver(id):

    @functools.wraps(meta_object_receiver)
    def receiver():
        from . import meta_relations
        return meta_relations.Event.create_from_id(id)

    return receiver


def event(name, value, text):
    return (name, value, text, meta_object_receiver(value))


class EVENT(rels_django.DjangoEnum):
    meta_object = rels.Column()

    records = (event('CREATED', 0, 'создание гильдии'),
               event('NEW_MEMBERSHIP_INVITE', 1, 'приглашение в гильдию'),
               event('NEW_MEMBERSHIP_REQUEST', 2, 'просьба вступить в гильдию'),
               event('MEMBERSHIP_INVITE_ACCEPTED', 3, 'приглашение в гильдию принято '),
               event('MEMBERSHIP_REQUEST_ACCEPTED', 4, 'просьба вступить в гильдию удовлетворена'),
               event('MEMBERSHIP_INVITE_REJECTED', 5, 'приглашение в гильдию отклонено'),
               event('MEMBERSHIP_REQUEST_REJECTED', 6, 'просьба вступить в гильдию отклонена'),
               event('MEMBER_LEFT', 7, 'игрок покинул гильдию'),
               event('MEMBER_REMOVED', 8, 'игрок исключён из гильдии'),
               event('TECHNICAL', 9, 'техническое сообщение'),
               event('ROLE_CHANGED', 10, 'изменение звания'),
               event('OWNER_CHANGED', 11, 'передача владения'),
               event('UPDATED', 12, 'редактирование гильдии'),
               event('EMISSARY_CREATED', 13, 'нанят эмиссар'),
               event('EMISSARY_DISSMISSED', 14, 'уволен эмиссар'),
               event('EMISSARY_KILLED', 15, 'убит эмиссар'),
               event('EMISSARY_MOVED', 16, 'перемещён эмиссар'),
               event('MEMBER_ADD_POINTS', 17, 'Хранитель внёс очки действия'),
               event('EMISSARY_DAMAGED', 18, 'покушение на эмиссара'),
               event('EMISSARY_EVENT_CREATED', 19, 'начало мероприятия'),
               event('EMISSARY_EVENT_CANCELED', 20, 'мероприятие отменено'),
               event('EMISSARY_EVENT_FINISHED', 21, 'мероприятие остановлено'),
               event('EMISSARY_RENAMED', 22, 'эмиссар сменил имя'),
               event('PROTECTORAT_ESTABLISHED', 23, 'установлен протекторат'),
               event('PROTECTORAT_LOST', 24, 'потерян протекторат'))


class PERMISSION(rels_django.DjangoEnum):
    on_member = rels.Column(unique=False)
    help = rels.Column(unique=False, single_type=False)
    in_development = rels.Column(unique=False)

    records = (('DESTROY', 0, 'Удаление гильдии', False, None, False),
               ('CHANGE_OWNER', 1, 'Передача владения гильдией', True, None, False),
               ('EDIT', 2, 'Редактирование гильдии', False, None, False),
               ('CHANGE_ROLE', 3, 'Изменение звания', True, 'Если старое и новое звание Хранителя меньше вашего', False),
               ('POLITICS', 4, 'Объявление войны/мира другой гильдии', False, None, True),
               ('EMISSARIES_RELOCATION', 5, 'Назначение/перемещение/увольнение эмиссаров', False, None, False),
               ('EMISSARIES_PLANING', 6, 'Управление мероприятиями эмиссаров', False, None, False),
               ('TAKE_MEMBER', 7, 'Принятие в гильдию', False, 'В звании рекрута', False),
               ('REMOVE_MEMBER', 8, 'Исключение из гильдии', True, 'Если ваше звание выше', False),
               ('FORUM_MODERATION', 9, 'Модерация гильдейского форума', False, None, True),
               ('RECEIVE_MESSAGES', 13, 'Получает личные сообщения о важных событиях', False, None, False),
               ('ACCESS_CHRONICLE', 10, 'Просмотр событий гильдии', False, None, False),
               ('BULK_MAILING', 11, 'Массовая рассылка сообщений', False, 'Отключён интерфейс', False),
               ('EMISSARIES_QUESTS', 12, 'Выполнение заданий эмиссаров', False, None, False))


class MEMBER_ROLE(rels_django.DjangoEnum):
    priority = rels.Column()
    symbol = rels.Column()
    permissions = rels.Column(unique=True, no_index=True)

    records = (('MASTER', 0, 'Магистр', 0, '♔',
                (PERMISSION.DESTROY,
                 PERMISSION.CHANGE_OWNER,
                 PERMISSION.EDIT,
                 PERMISSION.CHANGE_ROLE,
                 PERMISSION.POLITICS,
                 PERMISSION.EMISSARIES_RELOCATION,
                 PERMISSION.EMISSARIES_PLANING,
                 PERMISSION.EMISSARIES_QUESTS,
                 PERMISSION.TAKE_MEMBER,
                 PERMISSION.REMOVE_MEMBER,
                 PERMISSION.FORUM_MODERATION,
                 PERMISSION.ACCESS_CHRONICLE,
                 PERMISSION.BULK_MAILING,
                 PERMISSION.RECEIVE_MESSAGES)),

               ('COMANDOR', 2, 'Командор', 1, '♕',
                (PERMISSION.EDIT,
                 PERMISSION.CHANGE_ROLE,
                 PERMISSION.POLITICS,
                 PERMISSION.EMISSARIES_RELOCATION,
                 PERMISSION.EMISSARIES_PLANING,
                 PERMISSION.EMISSARIES_QUESTS,
                 PERMISSION.TAKE_MEMBER,
                 PERMISSION.REMOVE_MEMBER,
                 PERMISSION.FORUM_MODERATION,
                 PERMISSION.ACCESS_CHRONICLE,
                 PERMISSION.BULK_MAILING,
                 PERMISSION.RECEIVE_MESSAGES)),

               ('OFFICER', 3, 'Офицер', 2, '♖',
                (PERMISSION.EMISSARIES_PLANING,
                 PERMISSION.EMISSARIES_QUESTS,
                 PERMISSION.TAKE_MEMBER,
                 PERMISSION.REMOVE_MEMBER,
                 PERMISSION.FORUM_MODERATION,
                 PERMISSION.ACCESS_CHRONICLE,
                 PERMISSION.BULK_MAILING,
                 PERMISSION.RECEIVE_MESSAGES)),

               ('FIGHTER', 4, 'Боец', 3, '♘',
                (PERMISSION.EMISSARIES_QUESTS,
                 PERMISSION.ACCESS_CHRONICLE,
                 PERMISSION.BULK_MAILING)),

               ('RECRUIT', 1, 'Рекрут', 4, '♙',
                ()))


ROLES_TO_NOTIFY = [role
                   for role in MEMBER_ROLE.records
                   if PERMISSION.RECEIVE_MESSAGES in role.permissions]


class CURRENCY(rels_django.DjangoEnum):
    records = (('ACTION_POINTS', 0, 'очки действий'),
               ('FREE_QUESTS', 1, 'задания для неподписчиков'),
               ('EXPERIENCE', 2, 'опыт'))


class UPGRADABLE_PROPERTIES(rels_django.DjangoEnum):
    property = rels.Column()
    maximum = rels.Column(unique=False)
    experience = rels.Column(unique=False)
    delta = rels.Column(unique=False)

    records = (('FIGHTERS_MAXIMUM', 0, 'максимум членов гильдии', 'fighters_maximum_level',
                tt_clans_constants.FIGHTERS_MAXIMUM_LEVEL_STEPS,
                tt_clans_constants.FIGHTERS_MAXIMUM_LEVELS_EXPERIENCE,
                1),
               ('EMISSARIES_MAXIMUM', 1, 'максимум эмиссаров', 'emissary_maximum_level',
                tt_clans_constants.EMISSARY_MAXIMUM_LEVEL_STEPS,
                tt_clans_constants.EMISSARY_MEXIMUM_LEVELS_EXPERIENCE,
                1),
               ('POINTS_GAIN', 2, 'скорость прироста очков действия', 'points_gain_level',
                tt_clans_constants.POINTS_GAIN_LEVEL_STEPS,
                tt_clans_constants.POINTS_GAIN_LEVELS_EXPERIENCE,
                tt_clans_constants.POINTS_GAIN_INCREMENT_ON_LEVEL_UP),
               ('FREE_QUESTS_MAXIMUM', 3, 'максимум свободных заданий', 'free_quests_maximum_level',
                tt_clans_constants.FREE_QUESTS_MAXIMUM_LEVEL_STEPS,
                tt_clans_constants.FREE_QUESTS_MAXIMUM_LEVELS_EXPERIENCE,
                1),)
