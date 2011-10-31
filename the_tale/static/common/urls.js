
if (!window.pgf) {
    pgf = {};
}

pgf.urls = {
    'game:abilities:form': function(cardType){return '/game/abilities/'+cardType+'/form';},
    'game:abilities:activate': function(cardType){return '/game/abilities/'+cardType+'/activate';},
    'game:map:places:map_info': function(placeId){return '/game/map/places/'+placeId+'/map_info'}
};
