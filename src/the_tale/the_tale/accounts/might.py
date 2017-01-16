# coding: utf-8
import math

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


def get_linguistic_entity_info(entity_id, contribution_type, source):
    contributors = linguistics_prototypes.ContributionPrototype._db_filter(entity_id=entity_id,
                                                                           source=source,
                                                                           state=linguistics_relations.CONTRIBUTION_STATE.IN_GAME).order_by('created_at').values_list('type', 'account_id')

    author_type, author_id = contributors[0]

    contributors_count = sum(1 for type, a_id in contributors if type == contribution_type)

    if author_type == contribution_type:
        contributors_count -= 1

    return author_id, contributors_count


def calculate_linguistics_migth(account_id, contribution_type, might_per_added_entity, might_per_edited_entity, source):

    state = linguistics_relations.CONTRIBUTION_STATE.IN_GAME

    entities_ids = set(linguistics_prototypes.ContributionPrototype._db_filter(account_id=account_id,
                                                                               type=contribution_type,
                                                                               state=state,
                                                                               source=source).values_list('entity_id', flat=True))

    might = 0

    for entity_id in entities_ids:
        author_id, contributors_count = get_linguistic_entity_info(entity_id, contribution_type, source)

        if author_id == account_id:
            might += might_per_added_entity
        else:
            might += might_per_edited_entity / contributors_count

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

    might += Post.objects.filter(thread__subcategory__restricted=False,
                                 author_id=account.id,
                                 state=POST_STATE.DEFAULT).count() * relations.MIGHT_AMOUNT.FOR_FORUM_POST.amount
    might += Thread.objects.filter(subcategory__restricted=False,
                                   author_id=account.id).count() * relations.MIGHT_AMOUNT.FOR_FORUM_THREAD.amount

    might += Vote.objects.filter(owner_id=account.id).exclude(type=VOTE_TYPE.REFRAINED).count() * relations.MIGHT_AMOUNT.FOR_BILL_VOTE.amount
    might += Bill.objects.filter(owner_id=account.id, state=BILL_STATE.ACCEPTED).count() * relations.MIGHT_AMOUNT.FOR_BILL_ACCEPTED.amount

    might += calculate_linguistics_migth(account.id,
                                         contribution_type=linguistics_relations.CONTRIBUTION_TYPE.WORD,
                                         might_per_added_entity=relations.MIGHT_AMOUNT.FOR_ADDED_WORD_FOR_PLAYER.amount,
                                         might_per_edited_entity=relations.MIGHT_AMOUNT.FOR_EDITED_WORD_FOR_PLAYER.amount,
                                         source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)
    might += calculate_linguistics_migth(account.id,
                                         contribution_type=linguistics_relations.CONTRIBUTION_TYPE.WORD,
                                         might_per_added_entity=relations.MIGHT_AMOUNT.FOR_ADDED_WORD_FOR_MODERATOR.amount,
                                         might_per_edited_entity=relations.MIGHT_AMOUNT.FOR_EDITED_WORD_FOR_MODERATOR.amount,
                                         source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)
    might += calculate_linguistics_migth(account.id,
                                         contribution_type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE,
                                         might_per_added_entity=relations.MIGHT_AMOUNT.FOR_ADDED_TEMPLATE_FOR_PLAYER.amount,
                                         might_per_edited_entity=relations.MIGHT_AMOUNT.FOR_EDITED_TEMPLATE_FOR_PLAYER.amount,
                                         source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)
    might += calculate_linguistics_migth(account.id,
                                         contribution_type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE,
                                         might_per_added_entity=relations.MIGHT_AMOUNT.FOR_ADDED_TEMPLATE_FOR_MODERATOR.amount,
                                         might_per_edited_entity=relations.MIGHT_AMOUNT.FOR_EDITED_TEMPLATE_FOR_MODERATOR.amount,
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

    recalculate_folclor_rating()


def recalculate_folclor_rating():
    from the_tale.blogs import models as folclor_models

    for post in folclor_models.Post.objects.all().iterator():
        voters_ids = folclor_models.Vote.objects.filter(post_id=post.id).values_list('voter_id', flat=True)

        rating = 0

        for account in AccountPrototype._model_class.objects.filter(id__in=voters_ids).iterator():
            might = account.might
            if might is None or might < 100:
                might = 1
            else:
                might /= 100

            rating += math.log(might) * 100

        folclor_models.Post.objects.filter(id=post.id).update(rating=int(math.ceil(rating)))
