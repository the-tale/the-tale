
import smart_imports

smart_imports.all()


def prepair_forum():
    forum_category = forum_models.Category.objects.create(caption='category-1', slug='category-1')
    forum_models.SubCategory.objects.create(caption=conf.settings.FORUM_CATEGORY_UID + '-caption',
                                            uid=conf.settings.FORUM_CATEGORY_UID,
                                            category=forum_category)


def create_post_for_meta_object(author, caption, text, meta_object, vote_by=None):
    post = prototypes.PostPrototype.create(author, caption, text)
    meta_relations_logic.create_relations_for_objects(meta_relations.IsAbout,
                                                      meta_relations.Post.create_from_object(post),
                                                      [meta_object])
    if vote_by:
        prototypes.VotePrototype.create(post, voter=vote_by)
