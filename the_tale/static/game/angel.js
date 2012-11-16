if (!window.pgf) {
    pgf = {};
}

if (!pgf.game) {
    pgf.game = {};
}

if (!pgf.game.widgets) {
    pgf.game.widgets = {};
}

if (!pgf.game.events) {
    pgf.game.events = {};
}


pgf.game.widgets.Abilities = function(selector, widgets, params) {
    var instance = this;

    var abilities = pgf.game.data.abilities;

    var widget = jQuery(selector);
    var deckContainer = jQuery('.pgf-abilities-list', widget);
    var activateAbilityWidget = jQuery('#activate-ability-block');
    var activateAbilityFormWidget = jQuery('.pgf-activate-form', activateAbilityWidget);
    var tooltipTemplate = jQuery(params.tooltipTemplate);

    jQuery('.pgf-cancel', activateAbilityWidget).click(function(e){
        e.preventDefault();
        //TODO: replace with some kind of api not related to widgets
        widgets.switcher.ShowMapWidget();
    });
    var MINIMUM_LOCK_DELAY = 750;
    var abilitiesWaitingStartTimes = {};

    var angelEnergy = 0;
    var deck = {};
    var turn = {};

    var allowAbilityUnlock = {};

    function ChangeAbilityEnergyState(abilityType, energy) {
        jQuery('.pgf-ability-'+abilityType, widget).toggleClass('no-energy', energy);
    }

    function ToggleWait(ability, wait) {
        ability.spin(wait ? 'tiny' : false);
        ability.toggleClass('wait', wait).toggleClass('pgf-wait', wait);
    }

    function ChangeAbilityWaitingState(abilityType, wait) {
        var ability = jQuery('.pgf-ability-'+abilityType, widget);

        if (wait) {
            var date = new Date();
            abilitiesWaitingStartTimes[abilityType] = date.getTime();

            ToggleWait(ability, true);
        }
        else {
            var date = new Date();
            var curTime = date.getTime();
            var minCloseTime =  abilitiesWaitingStartTimes[abilityType] + MINIMUM_LOCK_DELAY;

            if ( minCloseTime <= curTime) {
                ToggleWait(ability, false);
            }
            else {
                window.setTimeout(function() { ToggleWait(ability, false); }, minCloseTime - curTime);
            }
        }
    }

    function IsProcessingAbility(abilityType) {
        return jQuery('.pgf-ability-'+abilityType, widget).hasClass('pgf-wait');
    }

    function ActivateAbility(ability) {

        var abilityInfo = abilities[ability.type];

        if (abilityInfo.cost > angelEnergy) {
            return;
        }

        if (IsProcessingAbility(ability.type)) {
            return;
        }

        ChangeAbilityWaitingState(ability.type, true);

        //TODO: replace with some kind of api not related to widgets
        var currentHero = widgets.heroes.CurrentHero();

        var heroId = -1;
        if (currentHero) {
            heroId = currentHero.id;
        }

        var ajax_data = {};
        if (heroId !== undefined) {
            ajax_data.hero_id = heroId;
        }
        pgf.forms.Post({action: pgf.urls['game:abilities:activate'](ability.type),
                        data: ajax_data,
                        wait: false,
                        OnError: function() {
                            ChangeAbilityWaitingState(ability.type, false);
                        },
                        OnSuccess: function(data) {
                            allowAbilityUnlock[ability.type] = true;
                            ability.available_at = data.data.available_at;
                            jQuery(document).trigger(pgf.game.events.DATA_REFRESH_NEEDED);
                        }
                       });
    }

    function RenderAbility(ability) {

        var abilityInfo = abilities[ability.type];
        var element = jQuery('.pgf-ability-'+abilityInfo.type.toLowerCase());

        ChangeAbilityEnergyState(ability.type, abilityInfo.cost > angelEnergy);

        element.click(function(e){
            e.preventDefault();
            ActivateAbility(ability);
        });
    }

    function RenderDeck() {
        for (var i in deck) {
            RenderAbility(deck[i]);
        }
    };

    function Refresh(game_data) {
        turn = game_data.turn;

        deck = game_data.abilities;
        angelEnergy = game_data.hero.energy.value;
    };

    function Render() {
        RenderDeck();
    };

    jQuery(document).bind(pgf.game.events.DATA_REFRESHED, function(e, game_data){
        Refresh(game_data);
        Render();

        for (abilityType in allowAbilityUnlock) {
            if (allowAbilityUnlock[abilityType]) {
                allowAbilityUnlock[abilityType] = false;
                ChangeAbilityWaitingState(abilityType, false);
            }
        }

    });
};
