# coding: utf-8
import random
from django.dispatch import receiver

from game.bills import signals as bills_signals
from game import signals as game_signals

from portal.newspaper.prototypes import NewspaperEventPrototype
from portal.newspaper import events


@receiver(bills_signals.bill_created, dispatch_uid="newspaper_bill_created")
def newspaper_bill_created(sender, bill, **kwargs):
    NewspaperEventPrototype.create(events.EventBillCreated(bill_id=bill.id, bill_type=bill.type.value, caption=bill.caption))


@receiver(bills_signals.bill_edited, dispatch_uid="newspaper_bill_edited")
def newspaper_bill_edited(sender, bill, **kwargs):
    NewspaperEventPrototype.create(events.EventBillEdited(bill_id=bill.id, bill_type=bill.type.value, caption=bill.caption))


@receiver(bills_signals.bill_processed, dispatch_uid="newspaper_bill_processed")
def newspaper_bill_processed(sender, bill, **kwargs):
    NewspaperEventPrototype.create(events.EventBillProcessed(bill_id=bill.id, bill_type=bill.type.value, caption=bill.caption, accepted=bill.state._is_ACCEPTED))

@receiver(bills_signals.bill_removed, dispatch_uid="newspaper_bill_removed")
def newspaper_bill_removed(sender, bill, **kwargs):
    NewspaperEventPrototype.create(events.EventBillRemoved(bill_id=bill.id, bill_type=bill.type.value, caption=bill.caption))


@receiver(game_signals.day_started, dispatch_uid='newspaper_day_started')
def newspaper_day_started(sender, **kwargs):
    from accounts.prototypes import AccountPrototype
    from game.heroes.prototypes import HeroPrototype
    from game.heroes.models import Hero

    heroes_number = Hero.objects.filter(is_fast=False).count()

    if heroes_number < 1:
        return

    hero_model = Hero.objects.filter(is_fast=False)[random.randint(0, heroes_number-1)]

    hero = HeroPrototype(model=hero_model)
    account = AccountPrototype.get_by_id(hero.account_id)

    NewspaperEventPrototype.create(events.EventHeroOfTheDay(hero_id=hero.id, hero_name=hero.name, race=hero.race,
                                                            gender=hero.gender, level=hero.level, power=hero.power,
                                                            account_id=account.id, nick=account.nick, might=hero.might))
