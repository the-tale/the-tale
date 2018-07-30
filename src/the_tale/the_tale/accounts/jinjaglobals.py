
import smart_imports

smart_imports.all()


@dext_jinja2.jinjaglobal
def login_page_url(next_url='/'):
    return dext_jinja2.Markup(logic.login_page_url(next_url))


@dext_jinja2.jinjaglobal
def login_url(next_url='/'):
    return dext_jinja2.Markup(logic.login_url(next_url))


@dext_jinja2.jinjaglobal
def logout_url():
    return dext_jinja2.Markup(logic.logout_url())


@dext_jinja2.jinjaglobal
def forum_complaint_theme():
    return conf.settings.FORUM_COMPLAINT_THEME


@dext_jinja2.jinjaglobal
def account_sidebar(user_account, page_account, page_caption, page_type, can_moderate=False):
    bills_count = bills_prototypes.BillPrototype.accepted_bills_count(page_account.id)

    threads_count = forum_models.Thread.objects.filter(author=page_account._model).count()

    threads_with_posts = forum_models.Thread.objects.filter(post__author=page_account._model).distinct().count()

    templates_count = linguistics_prototypes.ContributionPrototype._db_filter(account_id=page_account.id,
                                                                              type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE).count()

    words_count = linguistics_prototypes.ContributionPrototype._db_filter(account_id=page_account.id,
                                                                          type=linguistics_relations.CONTRIBUTION_TYPE.WORD).count()

    folclor_posts_count = blogs_models.Post.objects.filter(author=page_account._model, state=blogs_relations.POST_STATE.ACCEPTED).count()

    friendship = friends_prototypes.FriendshipPrototype.get_for_bidirectional(user_account, page_account)

    return dext_jinja2.Markup(dext_jinja2.render('accounts/sidebar.html',
                                                 context={'user_account': user_account,
                                                          'page_account': page_account,
                                                          'page_caption': page_caption,
                                                          'master_clan_info': clans_logic.ClanInfo(page_account),
                                                          'own_clan_info': clans_logic.ClanInfo(user_account),
                                                          'friendship': friendship,
                                                          'bills_count': bills_count,
                                                          'templates_count': templates_count,
                                                          'words_count': words_count,
                                                          'folclor_posts_count': folclor_posts_count,
                                                          'threads_count': threads_count,
                                                          'threads_with_posts': threads_with_posts,
                                                          'can_moderate': can_moderate,
                                                          'page_type': page_type,
                                                          'commission': conf.settings.MONEY_SEND_COMMISSION}))
