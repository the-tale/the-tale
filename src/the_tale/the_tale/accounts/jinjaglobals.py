# coding: utf-8

from dext.common.utils import jinja2

from the_tale.accounts import logic
from the_tale.accounts import conf


@jinja2.jinjaglobal
def login_page_url(next_url='/'):
    return jinja2.Markup(logic.login_page_url(next_url))

@jinja2.jinjaglobal
def login_url(next_url='/'):
    return jinja2.Markup(logic.login_url(next_url))

@jinja2.jinjaglobal
def logout_url():
    return jinja2.Markup(logic.logout_url())

@jinja2.jinjaglobal
def forum_complaint_theme():
    return conf.accounts_settings.FORUM_COMPLAINT_THEME


@jinja2.jinjaglobal
def account_sidebar(user_account, page_account, page_caption, page_type, can_moderate=False):
    from the_tale.forum.models import Thread
    from the_tale.game.bills.prototypes import BillPrototype
    from the_tale.linguistics.prototypes import ContributionPrototype
    from the_tale.linguistics.relations import CONTRIBUTION_TYPE
    from the_tale.accounts.friends.prototypes import FriendshipPrototype
    from the_tale.accounts.clans.logic import ClanInfo
    from the_tale.blogs.models import Post as BlogPost, POST_STATE as BLOG_POST_STATE

    bills_count = BillPrototype.accepted_bills_count(page_account.id)

    threads_count = Thread.objects.filter(author=page_account._model).count()

    threads_with_posts = Thread.objects.filter(post__author=page_account._model).distinct().count()

    templates_count = ContributionPrototype._db_filter(account_id=page_account.id,
                                                       type=CONTRIBUTION_TYPE.TEMPLATE).count()

    words_count = ContributionPrototype._db_filter(account_id=page_account.id,
                                                   type=CONTRIBUTION_TYPE.WORD).count()

    folclor_posts_count = BlogPost.objects.filter(author=page_account._model, state=BLOG_POST_STATE.ACCEPTED).count()

    friendship = FriendshipPrototype.get_for_bidirectional(user_account, page_account)

    return jinja2.Markup(jinja2.render('accounts/sidebar.html',
                                            context={'user_account': user_account,
                                                     'page_account': page_account,
                                                     'page_caption': page_caption,
                                                     'master_clan_info': ClanInfo(page_account),
                                                     'own_clan_info': ClanInfo(user_account),
                                                     'friendship': friendship,
                                                     'bills_count': bills_count,
                                                     'templates_count': templates_count,
                                                     'words_count': words_count,
                                                     'folclor_posts_count': folclor_posts_count,
                                                     'threads_count': threads_count,
                                                     'threads_with_posts': threads_with_posts,
                                                     'can_moderate': can_moderate,
                                                     'page_type': page_type,
                                                     'commission': conf.accounts_settings.MONEY_SEND_COMMISSION}))
