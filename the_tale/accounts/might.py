# coding: utf-8
import time

from django.db import models

from the_tale.accounts.models import Award
from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts import relations

from the_tale.forum.models import Post, Thread, POST_STATE
from the_tale.blogs.models import Post as BlogPost, POST_STATE as BLOG_POST_STATE

from the_tale.game.bills.models import Bill, Vote
from the_tale.game.bills.relations import BILL_STATE, VOTE_TYPE
from the_tale.game.phrase_candidates.models import PhraseCandidate, PHRASE_CANDIDATE_STATE
from the_tale.game.heroes.prototypes import HeroPrototype


def calculate_might(account): # pylint: disable=R0914

    MIGHT_FOR_FORUM_POST = 0.3
    MIGHT_FOR_FORUM_THREAD = 3
    MIGHT_FOR_BILL_VOTE = 1
    MIGHT_FOR_BILL_ACCEPTED = 33
    MIGHT_FOR_ADDED_PHRASE_CANDIDATE = 10
    MIGHT_FOR_GOOD_FOLCLOR_POST = 100

    MIGHT_FROM_REFERRAL = 0.1

    MIGHT_FOR_AWARD = { relations.AWARD_TYPE.BUG_MINOR: 111,
                        relations.AWARD_TYPE.BUG_NORMAL: 222,
                        relations.AWARD_TYPE.BUG_MAJOR: 333,
                        relations.AWARD_TYPE.CONTEST_1_PLACE: 1000,
                        relations.AWARD_TYPE.CONTEST_2_PLACE: 666,
                        relations.AWARD_TYPE.CONTEST_3_PLACE: 333,
                        relations.AWARD_TYPE.STANDARD_MINOR: 333,
                        relations.AWARD_TYPE.STANDARD_NORMAL: 666,
                        relations.AWARD_TYPE.STANDARD_MAJOR: 1000 }


    might = 0

    might += Post.objects.filter(author_id=account.id, state=POST_STATE.DEFAULT).count() * MIGHT_FOR_FORUM_POST
    might += Thread.objects.filter(author_id=account.id).count() * MIGHT_FOR_FORUM_THREAD

    might += Vote.objects.filter(owner_id=account.id).exclude(type=VOTE_TYPE.REFRAINED).count() * MIGHT_FOR_BILL_VOTE
    might += Bill.objects.filter(owner_id=account.id, state=BILL_STATE.ACCEPTED).count() * MIGHT_FOR_BILL_ACCEPTED

    might += PhraseCandidate.objects.filter(author_id=account.id, state=PHRASE_CANDIDATE_STATE.ADDED).count() * MIGHT_FOR_ADDED_PHRASE_CANDIDATE

    might += BlogPost.objects.filter(author_id=account.id, state=BLOG_POST_STATE.ACCEPTED, votes__gt=1).count() * MIGHT_FOR_GOOD_FOLCLOR_POST

    referrals_mights = AccountPrototype._model_class.objects.filter(referral_of=account.id).aggregate(models.Sum('might'))['might__sum']

    might += referrals_mights * MIGHT_FROM_REFERRAL if referrals_mights else 0

    for award_type, might_cooficient in MIGHT_FOR_AWARD.items():
        might += Award.objects.filter(account_id=account.id, type=award_type).count() * might_cooficient

    return might


def recalculate_accounts_might():

    for account_model in AccountPrototype.live_query():
        account = AccountPrototype(model=account_model)

        new_might = calculate_might(account)

        if account.might != new_might:
            account.set_might(new_might)
            HeroPrototype.get_by_account_id(account.id).cmd_update_with_account_data(account)

        time.sleep(0)
