
if (!window.pgf) {
    pgf = {};
}

pgf.urls = {
    'game:heroes:show': function(heroId){return '/game/heroes/'+heroId;},
    'game:heroes:choose_ability_dialog': function(heroId){return '/game/heroes/'+heroId+'/choose-ability-dialog';},
    'game:heroes:choose_ability': function(heroId, abilityId){return '/game/heroes/'+heroId+'/choose-ability?ability_id='+abilityId;},
    'game:abilities:activate': function(cardType, buildingId, battleId) {
        var url = '/game/abilities/'+cardType+'/activate';
        if (buildingId != undefined) {
            url = url + '?building=' + buildingId;
        }
        if (battleId != undefined) {
            url = url + '?battle=' + battleId;
        }
        return url;
    },
    'game:map:cell_info': function(x, y){return '/game/map/cell-info?x='+x+'&y='+y;},
    'guide:artifacts:info': function(id){return '/guide/artifacts/'+id+'/info';},
    'game:quests:choose': function(questId, choicePoint, choice) {
        return '/game/quests/'+questId+'/choose?choice_point='+choicePoint+'&choice='+choice;}
};
