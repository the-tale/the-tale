# coding: utf-8
import datetime

from django.db import models

from django.core.management.base import BaseCommand

from the_tale.accounts import models as accounts_models

from the_tale.bank import models as bank_models
from the_tale.bank import relations as bank_relations

from the_tale.forum import models as forum_models

from the_tale.game.bills import models as bills_models
from the_tale.game.bills import relations as bills_relations

from the_tale.blogs import models as folclor_models

from the_tale.linguistics import models as linguistics_models
from the_tale.linguistics import relations as linguistics_relations

from the_tale.accounts.clans import models as clans_models
from the_tale.accounts.clans import relations as clans_relations


MONETIZATION_STARTED_AT = datetime.date(year=2013, month=8, day=6)


def accounts_count(ids):
    return len(ids)

def posts_on_forum(ids):
    return forum_models.Post.objects.filter(author_id__in=ids).count()

def threads_on_forum(ids):
    return forum_models.Thread.objects.filter(author_id__in=ids).count()

def no_posts_on_forum(ids):
    return len(ids - set(forum_models.Post.objects.filter(author_id__in=ids).values_list('author_id', flat=True)))

def no_threads_on_forum(ids):
    return len(ids - set(forum_models.Thread.objects.filter(author_id__in=ids).values_list('author_id', flat=True)))

def has_posts_on_forum(ids):
    return len(set(forum_models.Post.objects.filter(author_id__in=ids).values_list('author_id', flat=True)))

def has_threads_on_forum(ids):
    return len(set(forum_models.Thread.objects.filter(author_id__in=ids).values_list('author_id', flat=True)))

def might(ids):
    return sum(accounts_models.Account.objects.filter(id__in=ids).values_list('might', flat=True))

def has_might(ids):
    return accounts_models.Account.objects.filter(id__in=ids, might__gt=0).count()

def no_might(ids):
    return accounts_models.Account.objects.filter(id__in=ids, might=0).count()

def bills_total(ids):
    return bills_models.Bill.objects.filter(owner_id__in=ids, created_at__gte=MONETIZATION_STARTED_AT).count()

def no_bills_total(ids):
    return len(ids - set(bills_models.Bill.objects.filter(created_at__gte=MONETIZATION_STARTED_AT).values_list('owner_id', flat=True)))

def has_bills_total(ids):
    return len(set(bills_models.Bill.objects.filter(owner_id__in=ids, created_at__gte=MONETIZATION_STARTED_AT).values_list('owner_id', flat=True)))

def bills_accepted(ids):
    return bills_models.Bill.objects.filter(owner_id__in=ids, created_at__gte=MONETIZATION_STARTED_AT, state=bills_relations.BILL_STATE.ACCEPTED).count()

def votes_total(ids):
    return bills_models.Vote.objects.filter(owner_id__in=ids, created_at__gte=MONETIZATION_STARTED_AT).count()

def no_votes_total(ids):
    return len(ids - set(bills_models.Vote.objects.filter(created_at__gte=MONETIZATION_STARTED_AT).values_list('owner_id', flat=True)))

def has_votes_total(ids):
    return len(set(bills_models.Vote.objects.filter(owner_id__in=ids, created_at__gte=MONETIZATION_STARTED_AT).values_list('owner_id', flat=True)))

def folclor_posts(ids):
    return folclor_models.Post.objects.filter(author_id__in=ids).count()

def folclor_votes(ids):
    return folclor_models.Vote.objects.filter(voter_id__in=ids).count()

def no_folclor_posts(ids):
    return len(ids - set(folclor_models.Post.objects.filter().values_list('author_id', flat=True)))

def has_folclor_posts(ids):
    return len(set(folclor_models.Post.objects.filter(author_id__in=ids).values_list('author_id', flat=True)))

def no_folclor_votes(ids):
    return len(ids - set(folclor_models.Vote.objects.filter().values_list('voter_id', flat=True)))

def has_folclor_votes(ids):
    return len(set(folclor_models.Vote.objects.filter(voter_id__in=ids).values_list('voter_id', flat=True)))

def linguistics_templates(ids):
    return linguistics_models.Contribution.objects.filter(account_id__in=ids, type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE).count()

def linguistics_has_templates(ids):
    return len(set(linguistics_models.Contribution.objects.filter(account_id__in=ids, type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE).values_list('account_id', flat=True)))

def linguistics_no_templates(ids):
    return len(ids - set(linguistics_models.Contribution.objects.filter(account_id__in=ids, type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE).values_list('account_id', flat=True)))

def linguistics_words(ids):
    return linguistics_models.Contribution.objects.filter(account_id__in=ids, type=linguistics_relations.CONTRIBUTION_TYPE.WORD).count()

def linguistics_has_words(ids):
    return len(set(linguistics_models.Contribution.objects.filter(account_id__in=ids, type=linguistics_relations.CONTRIBUTION_TYPE.WORD).values_list('account_id', flat=True)))

def linguistics_no_words(ids):
    return len(ids - set(linguistics_models.Contribution.objects.filter(account_id__in=ids, type=linguistics_relations.CONTRIBUTION_TYPE.WORD).values_list('account_id', flat=True)))

def clans_clanleads(ids):
    return clans_models.Membership.objects.filter(account_id__in=ids, role=clans_relations.MEMBER_ROLE.LEADER).count()

def clans_members(ids):
    return clans_models.Membership.objects.filter(account_id__in=ids, role=clans_relations.MEMBER_ROLE.MEMBER).count()

def clans_not_members(ids):
    return len(ids - set(clans_models.Membership.objects.filter(account_id__in=ids).values_list('account_id', flat=True)))


class Command(BaseCommand):

    help = 'statistics of benefits from different user kinds in relation to donate types '

    requires_model_validation = False

    def handle(self, *args, **options):

        all_accounts_ids = set(accounts_models.Account.objects.filter(is_fast=False).values_list('id', flat=True))
        donaters_ids = set(bank_models.Invoice.objects.filter(models.Q(state=bank_relations.INVOICE_STATE.CONFIRMED)|models.Q(state=bank_relations.INVOICE_STATE.FORCED),
                                                              sender_type=bank_relations.ENTITY_TYPE.XSOLLA).values_list('recipient_id', flat=True))
        not_donaters_ids = all_accounts_ids - donaters_ids
        premiums_ids = set(bank_models.Invoice.objects.filter(models.Q(state=bank_relations.INVOICE_STATE.CONFIRMED)|models.Q(state=bank_relations.INVOICE_STATE.FORCED),
                                                              operation_uid__contains='<subscription').values_list('recipient_id', flat=True))
        not_premiums_ids = donaters_ids - premiums_ids

        current_premiums_ids = set(accounts_models.Account.objects.filter(is_fast=False, premium_end_at__gt=datetime.datetime.now()).values_list('id', flat=True))

        accounts_sets = [(u'все аккаунты\t\t\t', all_accounts_ids),
                         (u'хоть раз платили\t\t', donaters_ids),
                         (u'ни разу не платили\t\t', not_donaters_ids),
                         (u'хоть раз купили подписку\t', premiums_ids),
                         (u'платили, но без подписки\t', not_premiums_ids),
                         (u'текущие подписчики\t\t', current_premiums_ids)]

        processors = [(u'количество', accounts_count, None, None),
                      (u'форум: сообщения', posts_on_forum, None, None),
                      (u'форум: темы', threads_on_forum, None, None),
                      (u'форум: есть сообщения', has_posts_on_forum, u'от всех', accounts_count),
                      (u'форум: нет сообщений', no_posts_on_forum, u'от всех', accounts_count),
                      (u'форум: есть темы', has_threads_on_forum, u'от всех', accounts_count),
                      (u'форум: нет тем', no_threads_on_forum, u'от всех', accounts_count),
                      (u'могущество всего', might, None, None),
                      (u'могущество != 0', has_might, u'от всех', accounts_count),
                      (u'могущество = 0', no_might, u'от всех', accounts_count),
                      (u'законы: всего (после 06.08.2013)', bills_total, None, None),
                      (u'законы: принятые (после 06.08.2013)', bills_accepted, None, None),
                      (u'законы: есть законы (после 06.08.2013)', has_bills_total, u'от всех', accounts_count),
                      (u'законы: нет законов (после 06.08.2013)', no_bills_total, u'от всех', accounts_count),
                      (u'голоса: всего (после 06.08.2013)', votes_total, None, None),
                      (u'голоса: есть голоса (после 06.08.2013)', has_votes_total, u'от всех', accounts_count),
                      (u'голоса: нет голосов (после 06.08.2013)', no_votes_total, u'от всех', accounts_count),
                      (u'фолклор: произведения', folclor_posts, None, None),
                      (u'фолклор: есть произведения', has_folclor_posts, u'от всех', accounts_count),
                      (u'фолклор: нет произведений', no_folclor_posts, u'от всех', accounts_count),
                      (u'фолклор: голоса', folclor_votes, None, None),
                      (u'фолклор: есть голоса', has_folclor_votes, u'от всех', accounts_count),
                      (u'фолклор: нет голосов', no_folclor_votes, u'от всех', accounts_count),
                      (u'лингвистика: вклад в шаблоны', linguistics_templates, None, None),
                      (u'лингвистика: есть шаблоны', linguistics_has_templates, u'от всех', accounts_count),
                      (u'лингвистика: нет шаблонов', linguistics_no_templates, u'от всех', accounts_count),
                      (u'лингвистика: вклад в слова', linguistics_words, None, None),
                      (u'лингвистика: есть слова', linguistics_has_words, u'от всех', accounts_count),
                      (u'лингвистика: нет слов', linguistics_no_words, u'от всех', accounts_count),
                      (u'гильдии: лидеры', clans_clanleads, u'от всех', accounts_count),
                      (u'гильдии: рядовые', clans_members, u'от всех', accounts_count),
                      (u'гильдии: не в гильдии', clans_not_members, u'от всех', accounts_count)]


        for processor_name, processor, compare_name, comparator in processors:
            print
            print u'----- %s -----' % processor_name
            total = None
            for set_name, set_ids in accounts_sets:
                value = processor(set_ids)
                if total is None:
                    total = value

                if comparator is None:
                    print set_name, value, '\t', str(round(100 * float(value) / total, 2)).zfill(5), '%'
                else:
                    compare_to_value = comparator(set_ids)
                    print set_name, value, '\t', str(round(100 * float(value) / total, 2)).zfill(5), '%', '\t', compare_name, round(100 * float(value) / compare_to_value, 2), '%'
