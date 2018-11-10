
import smart_imports

smart_imports.all()


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
               ('CREATED_AT_ASC', 13, 'дате создания▼', ('created_at', 'name')),               )


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


class EVENT(rels_django.DjangoEnum):
    meta_object = rels.Column()

    records = (('CREATED', 0, 'создание гильдии', meta_object_receiver(0)),
               ('NEW_MEMBERSHIP_INVITE', 1, 'приглашение в гильдию', meta_object_receiver(1)),
               ('NEW_MEMBERSHIP_REQUEST', 2, 'просьба вступить в гильдию', meta_object_receiver(2)),
               ('MEMBERSHIP_INVITE_ACCEPTED', 3, 'приглашение в гильдию принято ', meta_object_receiver(3)),
               ('MEMBERSHIP_REQUEST_ACCEPTED', 4, 'просьба вступить в гильдию удовлетворена', meta_object_receiver(4)),
               ('MEMBERSHIP_INVITE_REJECTED', 5, 'приглашение в гильдию отклонено', meta_object_receiver(5)),
               ('MEMBERSHIP_REQUEST_REJECTED', 6, 'просьба вступить в гильдию отклонена', meta_object_receiver(6)),
               ('MEMBER_LEFT', 7, 'игрок покинул гильдию', meta_object_receiver(7)),
               ('MEMBER_REMOVED', 8, 'игрок исключён из гильдии', meta_object_receiver(8)),
               ('TECHNICAL', 9, 'техническое сообщение', meta_object_receiver(9)),
               ('ROLE_CHANGED', 10, 'изменение звания', meta_object_receiver(10)),
               ('OWNER_CHANGED', 11, 'передача владения', meta_object_receiver(11)))


class PERMISSION(rels_django.DjangoEnum):
    on_member = rels.Column(unique=False)
    help = rels.Column(unique=False, single_type=False)
    in_development = rels.Column(unique=False)

    records = (('DESTROY', 0, 'Удаление гильдии', False, None, False),
               ('CHANGE_OWNER', 1, 'Передача владения гильдией', True, None, False),
               ('EDIT', 2, 'Редактирование гильдии', False, None, False),
               ('CHANGE_ROLE', 3, 'Изменение звания', True, 'Если старое и новое звание Хранителя меньше вашего', False),
               ('POLITICS', 4, 'Объявление войны/мира другой гильдии', False, None, True),
               ('EMISSARIES_RELOCATION', 5, 'Назначение/перемещение эмиссаров', False, None, True),
               ('EMISSARIES_PLANING', 6, 'Управление мероприятиями эмиссаров', False, None, True),
               ('TAKE_MEMBER', 7, 'Принятие в гильдию', False, 'В звании рекрута', False),
               ('REMOVE_MEMBER', 8, 'Исключение из гильдии', True, 'Если ваше звание выше', False),
               ('FORUM_MODERATION', 9, 'Модерация гильдейского форума', False, None, True),
               ('ACCESS_CHRONICLE', 10, 'Просмотр событий гильдии', False, None, False),
               ('BULK_MAILING', 11, 'Массовая рассылка сообщений', False, 'Отключён интерфейс', False))


class MEMBER_ROLE(rels_django.DjangoEnum):
    priority = rels.Column()
    permissions = rels.Column(unique=True, no_index=True)

    records = (('MASTER', 0, 'Магистр', 0,
                (PERMISSION.DESTROY,
                 PERMISSION.CHANGE_OWNER,
                 PERMISSION.EDIT,
                 PERMISSION.CHANGE_ROLE,
                 PERMISSION.POLITICS,
                 PERMISSION.EMISSARIES_RELOCATION,
                 PERMISSION.EMISSARIES_PLANING,
                 PERMISSION.TAKE_MEMBER,
                 PERMISSION.REMOVE_MEMBER,
                 PERMISSION.FORUM_MODERATION,
                 PERMISSION.ACCESS_CHRONICLE,
                 PERMISSION.BULK_MAILING)),

               ('COMANDOR', 2, 'Командор', 1,
                (PERMISSION.EDIT,
                 PERMISSION.CHANGE_ROLE,
                 PERMISSION.POLITICS,
                 PERMISSION.EMISSARIES_RELOCATION,
                 PERMISSION.EMISSARIES_PLANING,
                 PERMISSION.TAKE_MEMBER,
                 PERMISSION.REMOVE_MEMBER,
                 PERMISSION.FORUM_MODERATION,
                 PERMISSION.ACCESS_CHRONICLE,
                 PERMISSION.BULK_MAILING)),

               ('OFFICER', 3, 'Офицер', 2,
                (PERMISSION.EMISSARIES_PLANING,
                 PERMISSION.TAKE_MEMBER,
                 PERMISSION.REMOVE_MEMBER,
                 PERMISSION.FORUM_MODERATION,
                 PERMISSION.ACCESS_CHRONICLE,
                 PERMISSION.BULK_MAILING)),

               ('FIGHTER', 4, 'Боец', 3,
                (PERMISSION.ACCESS_CHRONICLE,
                 PERMISSION.BULK_MAILING)),

               ('RECRUIT', 1, 'Рекрут', 4,
                ()))
