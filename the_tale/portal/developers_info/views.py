# coding: utf-8
import itertools
import datetime

from dext.views import handler

from common.utils.decorators import staff_required
from common.utils.resources import Resource

from accounts.models import Account


class DevelopersInfoResource(Resource):

    @staff_required()
    def initialize(self, *args, **kwargs):
        super(DevelopersInfoResource, self).initialize(*args, **kwargs)

    @handler('', method='get')
    def index(self):

        accounts_total = Account.objects.all().count()
        accounts_registered = Account.objects.filter(is_fast=False).count()
        accounts_active = Account.objects.filter(is_fast=False, active_end_at__gt=datetime.datetime.now()).count()

        return self.template('developers_info/index.html',
                             {'accounts_total': accounts_total,
                              'accounts_registered': accounts_registered,
                              'accounts_active': accounts_active,
                              'page_type': 'index'})

    @handler('mobs-and-artifacts', method='get')
    def mobs_and_artifacts(self):
        from game.mobs.storage import mobs_storage
        from game.artifacts.storage import artifacts_storage
        from game.map.relations import TERRAIN
        from game.logic import DEFAULT_HERO_EQUIPMENT

        mobs_without_loot = []
        mobs_without_artifacts = []
        mobs_without_loot_on_first_level = []
        mobs_without_artifacts_on_first_level = []

        for mob in mobs_storage.get_available_mobs_list(level=999999):
            if not mob.loot:
                mobs_without_loot.append(mob)
            elif not any(loot.level == mob.level for loot in mob.loot):
                mobs_without_loot_on_first_level.append(mob)

            if not mob.artifacts:
                mobs_without_artifacts.append(mob)
            elif not any(artifact.level == mob.level for artifact in mob.artifacts):
                mobs_without_artifacts_on_first_level.append(mob)

        territory_levels_checks = [1, 2, 3, 5, 7, 10, 15, 20, 30, 50, 75, 100]

        mobs_by_territory = { terrain_str:[0]*len(territory_levels_checks) for terrain_str in TERRAIN._ID_TO_STR.values() }

        for mob in mobs_storage.get_available_mobs_list(level=999999):
            for terrain in mob.terrains:
                for i, level in enumerate(territory_levels_checks):
                    if level >= mob.level:
                        mobs_by_territory[TERRAIN._ID_TO_STR[terrain]][i] += 1

        del mobs_by_territory['WATER_SHOAL']
        del mobs_by_territory['WATER_DEEP']

        mobs_by_territory = sorted(mobs_by_territory.items(), key=lambda x: x[1][-1])


        artifacts_without_mobs = []

        for artifact in itertools.chain(artifacts_storage.artifacts, artifacts_storage.loot):
            if artifact.uuid not in DEFAULT_HERO_EQUIPMENT._ALL and artifact.mob is None:
                artifacts_without_mobs.append(artifact)

        return self.template('developers_info/mobs_and_artifacts.html',
                             {'page_type': 'mobs_and_artifacts',
                              'mobs_without_loot': mobs_without_loot,
                              'mobs_without_artifacts': mobs_without_artifacts,
                              'mobs_without_loot_on_first_level': mobs_without_loot_on_first_level,
                              'mobs_without_artifacts_on_first_level': mobs_without_artifacts_on_first_level,
                              'mobs_by_territory': mobs_by_territory,
                              'territory_levels_checks': territory_levels_checks,
                              'artifacts_without_mobs': artifacts_without_mobs})
