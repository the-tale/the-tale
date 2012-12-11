
if (!window.pgf) {
    pgf = {};
}

pgf.urls = {
    'game:heroes:show': function(heroId){return '/game/heroes/'+heroId;},
    'game:heroes:choose_ability_dialog': function(heroId){return '/game/heroes/'+heroId+'/choose-ability-dialog';},
    'game:heroes:choose_ability': function(heroId, abilityId){return '/game/heroes/'+heroId+'/choose-ability?ability_id='+abilityId;},
    'game:abilities:form': function(cardType){return '/game/abilities/'+cardType+'/form';},
    'game:abilities:activate': function(cardType){return '/game/abilities/'+cardType+'/activate';},
    // 'game:map:places:map_info': function(placeId){return '/game/map/places/'+placeId+'/map-info';},
    'game:map:cell_info': function(x, y){return '/game/map/cell-info?x='+x+'&y='+y;},
    'game:quests:choose': function(questId, choicePoint, choice) {
        return '/game/quests/'+questId+'/choose?choice_point='+choicePoint+'&choice='+choice;}
};
