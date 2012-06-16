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

pgf.game.events.ANGEL_DATA_REFRESHED = 'pgf-angel-data-refreshed';
pgf.game.events.ANGEL_DATA_REFRESH_NEEDED = 'pgf-angel-data-refresh-needed';

pgf.game.AngelUpdater = function(params) {

    var instance = this;

    this.data = {};

    this.Refresh = function() {
        
        jQuery.ajax({
            dataType: 'json',
            type: 'get',
            url: params.url,
            data: {}, 
            success: function(answer, request, status) {

                instance.data = answer.data;

                jQuery(document).trigger(pgf.game.events.ANGEL_DATA_REFRESHED, instance.data);
            },
            error: function() {
            },
            complete: function() {
            }
        });
    };

    jQuery(document).bind(pgf.game.events.ANGEL_DATA_REFRESH_NEEDED, function(e){
        instance.Refresh();
    });
};

pgf.game.widgets.Angel = function(selector, params) {

    var content = jQuery(selector);
    var data = undefined;

    function RenderAngel() {
        if (!data) return;

        jQuery('.pgf-energy', content).text(data.energy.value);
        jQuery('.pgf-max-energy', content).text(data.energy.max);

        jQuery('.pgf-energy-percents', content).width( (100 * data.energy.value / data.energy.max) + '%');
    };

    function Refresh(angel_data) {
        data = angel_data.angel;
    };

    function Render() {
        RenderAngel();
    };

    jQuery(document).bind(pgf.game.events.ANGEL_DATA_REFRESHED, function(e, angel_data){
        Refresh(angel_data);
        Render();
    });
};

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

    var angelId = undefined;
    var angelEnergy = 0;
    var deck = {};
    var turn = {};

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
            ajax_data.angel_id = angelId;
        }
        pgf.forms.Post({action: pgf.urls['game:abilities:activate'](ability.type),
                        data: ajax_data,
                        wait: false,
                        OnError: function() {
                            ChangeAbilityWaitingState(ability.type, false);                            
                        },
                        OnSuccess: function(data) {
                            ChangeAbilityWaitingState(ability.type, false);

                            ability.available_at = data.data.available_at;
                           
                            jQuery(document).trigger(pgf.game.events.ANGEL_DATA_REFRESH_NEEDED);
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
        RenderAbility(deck[0]);
    };

    function Refresh(event_data) {
        deck = event_data.angel.abilities;
        angelId = event_data.angel.id;
        angelEnergy = event_data.angel.energy.value;
        turn = event_data.turn;
    };

    function Render() {
        RenderDeck();
    };

    jQuery(document).bind(pgf.game.events.ANGEL_DATA_REFRESHED, function(e, event_data){
        Refresh(event_data);
        Render();
    });
};


