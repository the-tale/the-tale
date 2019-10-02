
import smart_imports

smart_imports.all()


class ClansTestsMixin(object):

    def prepair_forum_for_clans(self):
        self.forum_category = forum_prototypes.CategoryPrototype.create(caption='clan-category',
                                                                        slug=conf.settings.FORUM_CATEGORY_SLUG,
                                                                        order=0)

    def create_clan(self, owner, uid):
        return logic.create_clan(owner=owner,
                                 abbr='a-%d' % uid,
                                 name='name-%d' % uid,
                                 motto='motto-%d' % uid,
                                 description='[b]description-%d[/b]' % uid)
