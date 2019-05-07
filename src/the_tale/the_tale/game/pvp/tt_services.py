import smart_imports

smart_imports.all()


class MatchmakerClient(tt_api_matchmaker.Client):

    def protobuf_to_battle_request(self, pb_battle_request):
        return objects.BattleRequest(id=pb_battle_request.id,
                                     initiator_id=pb_battle_request.initiator_id,
                                     matchmaker_type=relations.MATCHMAKER_TYPE(pb_battle_request.matchmaker_type),
                                     created_at=datetime.datetime.fromtimestamp(pb_battle_request.created_at),
                                     updated_at=datetime.datetime.fromtimestamp(pb_battle_request.updated_at))

    def protobuf_to_battle(self, pb_battle):
        return objects.Battle(id=pb_battle.id,
                              matchmaker_type=relations.MATCHMAKER_TYPE(pb_battle.matchmaker_type),
                              participants_ids=list(pb_battle.participants_ids),
                              created_at=datetime.datetime.fromtimestamp(pb_battle.created_at))


matchmaker = MatchmakerClient(entry_point=conf.settings.TT_MATCHMAKER_ENTRY_POINT)
