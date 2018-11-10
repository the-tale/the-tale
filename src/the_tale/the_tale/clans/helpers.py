
import smart_imports

smart_imports.all()


class ClansTestsMixin(object):

    def create_clan(self, owner, uid):
        return logic.create_clan(owner=owner,
                                 abbr='a-%d' % uid,
                                 name='name-%d' % uid,
                                 motto='motto-%d' % uid,
                                 description='[b]description-%d[/b]' % uid)
