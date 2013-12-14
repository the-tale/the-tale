
if (!window.pgf) {
    pgf = {};
}

pgf.urls = {
    'game:heroes:show': function(heroId){return '/game/heroes/'+heroId;},
    'game:heroes:choose_ability_dialog': function(heroId){return '/game/heroes/'+heroId+'/choose-ability-dialog';},
    'game:heroes:choose_ability': function(heroId, abilityId){return '/game/heroes/'+heroId+'/choose-ability?ability_id='+abilityId;},
    'game:abilities:use': function(cardType, buildingId, battleId) {
        var url = '/game/abilities/'+cardType+'/api/use?api_version=1.0&api_client='+API_CLIENT;
        if (buildingId != undefined) {
            url = url + '&building=' + buildingId;
        }
        if (battleId != undefined) {
            url = url + '&battle=' + battleId;
        }
        return url;
    },
    'game:map:cell_info': function(x, y){return '/game/map/cell-info?x='+x+'&y='+y;},
    'guide:artifacts:info': function(id){return '/guide/artifacts/'+id+'/info';}
};
