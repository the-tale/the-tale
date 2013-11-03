# coding: utf-8

from the_tale.accounts.clans.prototypes import ClanPrototype


class ClansTestsMixin(object):

    def create_clan(self, owner, i):
        return ClanPrototype.create(owner=owner,
                                    abbr=u'a-%d' % i,
                                    name=u'name-%d' % i,
                                    motto=u'motto-%d' %i ,
                                    description=u'[b]description-%d[/b]' % i)
