# coding: utf-8
import time
import collections

from django.db import models

from the_tale.accounts.models import Award
from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts import relations

from the_tale.forum.models import Post, Thread, POST_STATE
from the_tale.blogs.models import Post as BlogPost, POST_STATE as BLOG_POST_STATE

from the_tale.game.bills.models import Bill, Vote
from the_tale.game.bills.relations import BILL_STATE, VOTE_TYPE
from the_tale.game.heroes.prototypes import HeroPrototype

from the_tale.linguistics.prototypes import ContributionPrototype
from the_tale.linguistics.relations import CONTRIBUTION_TYPE


def calculate_linguistics_migth(account_id, contribution_type, might_per_entity):

    entities_ids = ContributionPrototype._db_filter(account_id=account_id,
                                                    type=contribution_type).values_list('entity_id', flat=True)

    contributions_per_entity = collections.Counter(ContributionPrototype._db_filter(type=contribution_type,
                                                                                    entity_id__in=entities_ids).values_list('entity_id', flat=True))

    might = 0

    might_per_entity = float(might_per_entity)

    for contributions_count in contributions_per_entity.values():
        might += might_per_entity / contributions_count

    return might


def calculate_might(account): # pylint: disable=R0914

    MIGHT_FROM_REFERRAL = 0.1

    might = 0

    might += Post.objects.filter(author_id=account.id, state=POST_STATE.DEFAULT).count() * relations.MIGHT_AMOUNT.FOR_FORUM_POST.amount
    might += Thread.objects.filter(author_id=account.id).count() * relations.MIGHT_AMOUNT.FOR_FORUM_THREAD.amount

    might += Vote.objects.filter(owner_id=account.id).exclude(type=VOTE_TYPE.REFRAINED).count() * relations.MIGHT_AMOUNT.FOR_BILL_VOTE.amount
    might += Bill.objects.filter(owner_id=account.id, state=BILL_STATE.ACCEPTED).count() * relations.MIGHT_AMOUNT.FOR_BILL_ACCEPTED.amount

    might += calculate_linguistics_migth(account.id, contribution_type=CONTRIBUTION_TYPE.WORD, might_per_entity=relations.MIGHT_AMOUNT.FOR_ADDED_WORD.amount)
    might += calculate_linguistics_migth(account.id, contribution_type=CONTRIBUTION_TYPE.TEMPLATE, might_per_entity=relations.MIGHT_AMOUNT.FOR_ADDED_TEMPLATE.amount)

    might += BlogPost.objects.filter(author_id=account.id, state=BLOG_POST_STATE.ACCEPTED, votes__gt=1).count() * relations.MIGHT_AMOUNT.FOR_GOOD_FOLCLOR_POST.amount

    referrals_mights = AccountPrototype._model_class.objects.filter(referral_of=account.id).aggregate(models.Sum('might'))['might__sum']

    might += referrals_mights * MIGHT_FROM_REFERRAL if referrals_mights else 0

    for award_type in relations.AWARD_TYPE.records:
        might += Award.objects.filter(account_id=account.id, type=award_type).count() * relations.MIGHT_AMOUNT.index_award[award_type][0].amount

    return might


def recalculate_accounts_might():

    for account_model in AccountPrototype.live_query():
        account = AccountPrototype(model=account_model)

        new_might = calculate_might(account)

        if account.might != new_might:
            account.set_might(new_might)
            HeroPrototype.get_by_account_id(account.id).cmd_update_with_account_data(account)

        time.sleep(0)
