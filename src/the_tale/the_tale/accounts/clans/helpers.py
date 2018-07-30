
import smart_imports

smart_imports.all()


class ClansTestsMixin(object):

    def create_clan(self, owner, i):
        return prototypes.ClanPrototype.create(owner=owner,
                                               abbr='a-%d' % i,
                                               name='name-%d' % i,
                                               motto='motto-%d' % i,
                                               description='[b]description-%d[/b]' % i)
