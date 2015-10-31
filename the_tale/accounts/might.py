# coding: utf-8
import time
import collections

from django.db import models
from django.utils.html import strip_tags

from the_tale.accounts.models import Award
from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts import relations

from the_tale.forum.models import Post, Thread, POST_STATE
from the_tale.blogs.relations import POST_STATE as BLOG_POST_STATE
from the_tale.blogs.prototypes import PostPrototype as BlogPostProtype
from the_tale.blogs import conf as blogs_conf

from the_tale.game.bills.models import Bill, Vote
from the_tale.game.bills.relations import BILL_STATE, VOTE_TYPE

from the_tale.linguistics import prototypes as linguistics_prototypes
from the_tale.linguistics import relations as linguistics_relations


def calculate_linguistics_migth(account_id, contribution_type, might_per_entity, source):

    entities_ids = linguistics_prototypes.ContributionPrototype._db_filter(account_id=account_id,
                                                                           type=contribution_type,
                                                                           source=source).values_list('entity_id', flat=True)

    state = linguistics_relations.CONTRIBUTION_STATE.IN_GAME

    contributions_per_entity = collections.Counter(linguistics_prototypes.ContributionPrototype._db_filter(type=contribution_type,
                                                                                                           entity_id__in=entities_ids,
                                                                                                           source=source,
                                                                                                           state=state).values_list('entity_id', flat=True))

    might = 0

    might_per_entity = float(might_per_entity)

    for contributions_count in contributions_per_entity.values():
        might += might_per_entity / contributions_count

    return might


def folclor_post_might(characters_count):
    might = relations.MIGHT_AMOUNT.FOR_MIN_FOLCLOR_POST.amount

    characters_count -= blogs_conf.settings.MIN_TEXT_LENGTH

    might += min(float(characters_count) / blogs_conf.settings.MIN_TEXT_LENGTH, 2) * relations.MIGHT_AMOUNT.FOR_MIN_FOLCLOR_POST.amount * 0.5

    characters_count -= 2 * blogs_conf.settings.MIN_TEXT_LENGTH

    if characters_count < 0:
        return might

    might += float(characters_count) / blogs_conf.settings.MIN_TEXT_LENGTH * relations.MIGHT_AMOUNT.FOR_MIN_FOLCLOR_POST.amount * 0.1

    return might


def calculate_might(account): # pylint: disable=R0914

    MIGHT_FROM_REFERRAL = 0.1

    might = 0

    might += Post.objects.filter(author_id=account.id, state=POST_STATE.DEFAULT).count() * relations.MIGHT_AMOUNT.FOR_FORUM_POST.amount
    might += Thread.objects.filter(author_id=account.id).count() * relations.MIGHT_AMOUNT.FOR_FORUM_THREAD.amount

    might += Vote.objects.filter(owner_id=account.id).exclude(type=VOTE_TYPE.REFRAINED).count() * relations.MIGHT_AMOUNT.FOR_BILL_VOTE.amount
    might += Bill.objects.filter(owner_id=account.id, state=BILL_STATE.ACCEPTED).count() * relations.MIGHT_AMOUNT.FOR_BILL_ACCEPTED.amount

    might += calculate_linguistics_migth(account.id,
                                         contribution_type=linguistics_relations.CONTRIBUTION_TYPE.WORD,
                                         might_per_entity=relations.MIGHT_AMOUNT.FOR_ADDED_WORD_FOR_PLAYER.amount,
                                         source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)
    might += calculate_linguistics_migth(account.id,
                                         contribution_type=linguistics_relations.CONTRIBUTION_TYPE.WORD,
                                         might_per_entity=relations.MIGHT_AMOUNT.FOR_ADDED_WORD_FOR_MODERATOR.amount,
                                         source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)
    might += calculate_linguistics_migth(account.id,
                                         contribution_type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE,
                                         might_per_entity=relations.MIGHT_AMOUNT.FOR_ADDED_TEMPLATE_FOR_PLAYER.amount,
                                         source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)
    might += calculate_linguistics_migth(account.id,
                                         contribution_type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE,
                                         might_per_entity=relations.MIGHT_AMOUNT.FOR_ADDED_TEMPLATE_FOR_MODERATOR.amount,
                                         source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)

    folclor_posts = BlogPostProtype.from_query(BlogPostProtype._db_filter(author_id=account.id, state=BLOG_POST_STATE.ACCEPTED))
    folclor_texts = (strip_tags(post.text_html) for post in folclor_posts)

    for text in folclor_texts:
        characters_count = len(text)
        might += folclor_post_might(characters_count)

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
            account.cmd_update_hero()

        time.sleep(0)
