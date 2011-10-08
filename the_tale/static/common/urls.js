
if (!window.pgf) {
    pgf = {};
}

pgf.urls = {
    'game:abilities:form': function(cardType){return '/game/abilities/'+cardType+'/form';},
    'game:abilities:activate': function(cardType){return '/game/abilities/'+cardType+'/activate';}
};
