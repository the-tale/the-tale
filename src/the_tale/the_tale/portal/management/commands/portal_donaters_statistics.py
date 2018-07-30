
import smart_imports

smart_imports.all()


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
    return blogs_models.Post.objects.filter(author_id__in=ids).count()


def folclor_votes(ids):
    return blogs_models.Vote.objects.filter(voter_id__in=ids).count()


def no_folclor_posts(ids):
    return len(ids - set(blogs_models.Post.objects.filter().values_list('author_id', flat=True)))


def has_folclor_posts(ids):
    return len(set(blogs_models.Post.objects.filter(author_id__in=ids).values_list('author_id', flat=True)))


def no_folclor_votes(ids):
    return len(ids - set(blogs_models.Vote.objects.filter().values_list('voter_id', flat=True)))


def has_folclor_votes(ids):
    return len(set(blogs_models.Vote.objects.filter(voter_id__in=ids).values_list('voter_id', flat=True)))


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


class Command(django_management.BaseCommand):

    help = 'statistics of benefits from different user kinds in relation to donate types '

    requires_model_validation = False

    def handle(self, *args, **options):

        all_accounts_ids = set(accounts_models.Account.objects.filter(is_fast=False).values_list('id', flat=True))
        donaters_ids = set(bank_models.Invoice.objects.filter(django_models.Q(state=bank_relations.INVOICE_STATE.CONFIRMED) | django_models.Q(state=bank_relations.INVOICE_STATE.FORCED),
                                                              sender_type=bank_relations.ENTITY_TYPE.XSOLLA).values_list('recipient_id', flat=True))
        not_donaters_ids = all_accounts_ids - donaters_ids
        premiums_ids = set(bank_models.Invoice.objects.filter(django_models.Q(state=bank_relations.INVOICE_STATE.CONFIRMED) | django_models.Q(state=bank_relations.INVOICE_STATE.FORCED),
                                                              operation_uid__contains='<subscription').values_list('recipient_id', flat=True))
        not_premiums_ids = donaters_ids - premiums_ids

        current_premiums_ids = set(accounts_models.Account.objects.filter(is_fast=False, premium_end_at__gt=datetime.datetime.now()).values_list('id', flat=True))

        accounts_sets = [('все аккаунты', all_accounts_ids),
                         ('хоть раз платили', donaters_ids),
                         ('ни разу не платили', not_donaters_ids),
                         ('хоть раз купили подписку', premiums_ids),
                         ('платили, но без подписки', not_premiums_ids),
                         ('текущие подписчики', current_premiums_ids)]

        processors = [('количество', accounts_count, None, None),
                      ('форум: сообщения', posts_on_forum, None, None),
                      ('форум: темы', threads_on_forum, None, None),
                      ('форум: есть сообщения', has_posts_on_forum, 'от всех', accounts_count),
                      ('форум: нет сообщений', no_posts_on_forum, 'от всех', accounts_count),
                      ('форум: есть темы', has_threads_on_forum, 'от всех', accounts_count),
                      ('форум: нет тем', no_threads_on_forum, 'от всех', accounts_count),
                      ('могущество всего', might, None, None),
                      ('могущество != 0', has_might, 'от всех', accounts_count),
                      ('могущество = 0', no_might, 'от всех', accounts_count),
                      ('записи: всего (после 06.08.2013)', bills_total, None, None),
                      ('записи: принятые (после 06.08.2013)', bills_accepted, None, None),
                      ('записи: есть записи (после 06.08.2013)', has_bills_total, 'от всех', accounts_count),
                      ('записи: нет записей (после 06.08.2013)', no_bills_total, 'от всех', accounts_count),
                      ('голоса: всего (после 06.08.2013)', votes_total, None, None),
                      ('голоса: есть голоса (после 06.08.2013)', has_votes_total, 'от всех', accounts_count),
                      ('голоса: нет голосов (после 06.08.2013)', no_votes_total, 'от всех', accounts_count),
                      ('фолклор: произведения', folclor_posts, None, None),
                      ('фолклор: есть произведения', has_folclor_posts, 'от всех', accounts_count),
                      ('фолклор: нет произведений', no_folclor_posts, 'от всех', accounts_count),
                      ('фолклор: голоса', folclor_votes, None, None),
                      ('фолклор: есть голоса', has_folclor_votes, 'от всех', accounts_count),
                      ('фолклор: нет голосов', no_folclor_votes, 'от всех', accounts_count),
                      ('лингвистика: вклад в шаблоны', linguistics_templates, None, None),
                      ('лингвистика: есть шаблоны', linguistics_has_templates, 'от всех', accounts_count),
                      ('лингвистика: нет шаблонов', linguistics_no_templates, 'от всех', accounts_count),
                      ('лингвистика: вклад в слова', linguistics_words, None, None),
                      ('лингвистика: есть слова', linguistics_has_words, 'от всех', accounts_count),
                      ('лингвистика: нет слов', linguistics_no_words, 'от всех', accounts_count),
                      ('гильдии: лидеры', clans_clanleads, 'от всех', accounts_count),
                      ('гильдии: рядовые', clans_members, 'от всех', accounts_count),
                      ('гильдии: не в гильдии', clans_not_members, 'от всех', accounts_count)]

        for processor_name, processor, compare_name, comparator in processors:
            print()
            print('----- %s -----' % processor_name)
            total = None
            for set_name, set_ids in accounts_sets:
                value = processor(set_ids)
                if total is None:
                    total = value

                if comparator is None:
                    message = '{:<30} {:>8} {:>8}%'
                    print(message.format(set_name, value, str(round(100 * float(value) / total, 2)).zfill(5)))
                else:
                    message = '{:<30} {:>8} {:>8}% {:>10} {}%'
                    compare_to_value = comparator(set_ids)
                    print(message.format(set_name, value, str(round(100 * float(value) / total, 2)).zfill(5), compare_name, round(100 * float(value) / compare_to_value, 2),))
