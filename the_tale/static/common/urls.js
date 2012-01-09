
if (!window.pgf) {
    pgf = {};
}

pgf.urls = {
    'game:heroes:': function(heroId){return '/game/heroes/'+heroId},
    'game:abilities:form': function(cardType){return '/game/abilities/'+cardType+'/form';},
    'game:abilities:activate': function(cardType){return '/game/abilities/'+cardType+'/activate';},
    'game:map:places:map_info': function(placeId){return '/game/map/places/'+placeId+'/map_info'},
    'game:quests:choose': function(questId, subquestId, choicePoint, choice) {
        return '/game/quests/'+questId+'/choose?subquest='+subquestId+'&choice_point='+choicePoint+'&choice='+choice;}
};
