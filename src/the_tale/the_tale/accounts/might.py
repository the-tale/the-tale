
import smart_imports

smart_imports.all()


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


def calculate_might(account):  # pylint: disable=R0914

    MIGHT_FROM_REFERRAL = 0.1

    might = 0

    forum_posts_query = forum_models.Post.objects.filter(thread__subcategory__restricted=False,
                                                         author_id=account.id,
                                                         state=forum_relations.POST_STATE.DEFAULT)
    forum_posts_query = forum_posts_query.exclude(thread__subcategory__uid=portal_conf.settings.FORUM_GAMES_SUBCATEGORY)

    might += forum_posts_query.count() * relations.MIGHT_AMOUNT.FOR_FORUM_POST.amount

    forum_threads_query = forum_models.Thread.objects.filter(subcategory__restricted=False,
                                                             author_id=account.id)
    forum_threads_query = forum_threads_query.exclude(subcategory__uid=portal_conf.settings.FORUM_GAMES_SUBCATEGORY)

    might += forum_threads_query.count() * relations.MIGHT_AMOUNT.FOR_FORUM_THREAD.amount

    might += bills_models.Vote.objects.filter(owner_id=account.id).exclude(type=bills_relations.VOTE_TYPE.REFRAINED).count() * relations.MIGHT_AMOUNT.FOR_BILL_VOTE.amount

    might += bills_models.Bill.objects.filter(owner_id=account.id, state=bills_relations.BILL_STATE.ACCEPTED).count() * relations.MIGHT_AMOUNT.FOR_BILL_ACCEPTED.amount

    might += bills_models.Moderation.objects.filter(moderator_id=account.id).order_by('bill_id').distinct('bill_id').count() * relations.MIGHT_AMOUNT.FOR_BILL_MODERATION.amount

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

    folclor_posts = blogs_prototypes.PostPrototype.from_query(blogs_prototypes.PostPrototype._db_filter(author_id=account.id, state=blogs_relations.POST_STATE.ACCEPTED))
    folclor_texts = (django_html.strip_tags(post.text_html) for post in folclor_posts)

    for text in folclor_texts:
        characters_count = len(text)
        might += folclor_post_might(characters_count)

    referrals_mights = prototypes.AccountPrototype._model_class.objects.filter(referral_of=account.id).aggregate(django_models.Sum('might'))['might__sum']

    might += referrals_mights * MIGHT_FROM_REFERRAL if referrals_mights else 0

    for award_type in relations.AWARD_TYPE.records:
        might += models.Award.objects.filter(account_id=account.id, type=award_type).count() * relations.MIGHT_AMOUNT.index_award[award_type][0].amount

    return might


def recalculate_account_might(account):
    new_might = calculate_might(account)

    if account.might == new_might:
        return

    account.set_might(new_might)
    account.cmd_update_hero()

    portal_logic.sync_with_discord(account)


def recalculate_accounts_might():

    for account_model in prototypes.AccountPrototype.live_query():
        account = prototypes.AccountPrototype(model=account_model)
        recalculate_account_might(account)

    recalculate_folclor_rating()


def recalculate_folclor_rating():
    for post in blogs_models.Post.objects.all().iterator():
        voters_ids = blogs_models.Vote.objects.filter(post_id=post.id).values_list('voter_id', flat=True)

        rating = 0

        for account in prototypes.AccountPrototype._model_class.objects.filter(id__in=voters_ids).iterator():
            might = account.might
            if might is None or might < 100:
                might = 1
            else:
                might /= 100

            rating += math.log(might) * 100

        blogs_models.Post.objects.filter(id=post.id).update(rating=int(math.ceil(rating)))
