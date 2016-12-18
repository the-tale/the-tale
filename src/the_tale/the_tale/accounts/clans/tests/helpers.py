# coding: utf-8

from the_tale.accounts.clans.prototypes import ClanPrototype


class ClansTestsMixin(object):

    def create_clan(self, owner, i):
        return ClanPrototype.create(owner=owner,
                                    abbr='a-%d' % i,
                                    name='name-%d' % i,
                                    motto='motto-%d' %i ,
                                    description='[b]description-%d[/b]' % i)
