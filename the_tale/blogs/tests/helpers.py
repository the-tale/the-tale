# coding: utf-8

from dext.common.meta_relations import logic as meta_relations_logic

from the_tale.forum.models import Category, SubCategory

from .. import conf
from .. import prototypes
from .. import meta_relations

def prepair_forum():
    forum_category = Category.objects.create(caption='category-1', slug='category-1')
    SubCategory.objects.create(caption=conf.settings.FORUM_CATEGORY_UID + '-caption',
                               uid=conf.settings.FORUM_CATEGORY_UID,
                               category=forum_category)

def create_post_for_meta_object(author, caption, text, meta_object, vote_by=None):
    post = prototypes.PostPrototype.create(author, caption, text)
    meta_relations_logic.create_relations_for_objects(meta_relations.IsAbout,
                                                      meta_relations.Post.create_from_object(post),
                                                      [meta_object])
    if vote_by:
        prototypes.VotePrototype.create(post, voter=vote_by)
