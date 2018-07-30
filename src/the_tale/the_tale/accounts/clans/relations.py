
import smart_imports

smart_imports.all()


class MEMBER_ROLE(rels_django.DjangoEnum):
    priority = rels.Column()
    records = (('LEADER', 0, 'лидер', 0),
               ('MEMBER', 1, 'рядовой', 1))


class ORDER_BY(rels_django.DjangoEnum):
    order_field = rels.Column()

    records = (('NAME', 0, 'имени', 'name'),
               ('ABBR', 1, 'аббревиатуре', 'abbr'),
               ('MEMBERS_NUMBER', 2, 'количеству героев', 'members_number'),
               ('CREATED_AT', 3, 'дате создания', 'created_at'),)


class MEMBERSHIP_REQUEST_TYPE(rels_django.DjangoEnum):
    records = (('FROM_CLAN', 0, 'от гильдии'),
               ('FROM_ACCOUNT', 1, 'от аккаунта'))


class PAGE_ID(rels_django.DjangoEnum):
    records = (('INDEX', 0, 'индексная страница'),
               ('NEW', 1, 'создание гильдии'),
               ('SHOW', 2, 'страница гильдии'),
               ('EDIT', 3, 'редактирование гильдии'),
               ('FOR_CLAN', 4, 'заявки в гильдию'),
               ('FOR_ACCOUNT', 5, 'предложения вступить в гильдию'))
