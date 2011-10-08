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
pgf.game.events.ANGEL_DATA_REFRESH_NEEDED = 'pgf-angel-data-refresh-needed'

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

        jQuery('.pgf-name', content).text(data.name);
        jQuery('.pgf-energy-current', content).text(data.energy.value);
        jQuery('.pgf-energy-maximum', content).text(data.energy.max);
        jQuery('.pgf-energy-regeneration', content).text(data.energy.regen);

        pgf.base.UpdateStatsBar(jQuery('.pgf-energy-bar', content), data.energy.max, data.energy.value);
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

    var angelId = undefined;
    var deck = {};
    var turn = {};

    function SetCooldown(abilityType) {
        jQuery('.ability-'+abilityType, widget).toggleClass('cooldown', true);
    }

    function ActivateAbility(ability) {

        if (ability.cooldown_end > turn.number) {
            return;
        }
        
        var abilityInfo = abilities[ability.type];

        //TODO: replace with some kind of api not related to widgets
        var currentHero = widgets.heroes.CurrentHero();

        var heroId = -1;
        if (currentHero) {
            heroId = currentHero.id;
        }

        if (abilityInfo.use_form) { 

            //TODO: replace with some kind of api not related to widgets
            widgets.switcher.ShowActivateAbilityWidget();

            function OnSuccessActivation(form, data) {
                ability.cooldown_end = data.data.cooldown_end;
                if (ability.cooldown_end) SetCooldown(ability.type);

                //TODO: replace with some kind of api not related to widgets
                widgets.switcher.ShowMapWidget();

                jQuery(document).trigger(pgf.game.events.ANGEL_DATA_REFRESH_NEEDED);
            }

            jQuery.ajax({
                type: 'get',
                url: pgf.urls['game:abilities:form'](ability.type),
                success: function(data, request, status) {
                    activateAbilityFormWidget.html(data);

                    formSelector = jQuery('form', activateAbilityFormWidget);

                    jQuery('#id_angel_id', formSelector).val(angelId);
                    jQuery('#id_hero_id', formSelector).val(heroId);

                    var activationForm = new pgf.forms.Form(formSelector,
                                                            {action: pgf.urls['game:abilities:activate'](ability.type),
                                                             OnSuccess: OnSuccessActivation});
                },
                error: function(request, status, error) {
                },
                complete: function(request, status) {
                }
            });
        }
        else {
            var ajax_data = {};
            if (heroId !== undefined) {
                ajax_data.hero = heroId;
            }
            pgf.forms.Post({action: pgf.urls['game:abilities:activate'](ability.type),
                            data: ajax_data,
                            OnSuccess: function(data) {
                                ability.cooldown_end = data.data.cooldown_end;
                                if (ability.cooldown_end) SetCooldown(ability.cooldown_end);
                            }
                           });
        }
        
    }

    function RenderAbilityTootltip(tooltip, ability) {
        var abilityInfo = abilities[ability.type]
        jQuery('.pgf-name', tooltip).text(abilityInfo.name);
        jQuery('.pgf-description', tooltip).text(abilityInfo.description);
        jQuery('.pgf-artistic', tooltip).text(abilityInfo.artistic);

        return tooltip;
    };

    function RenderAbility(index, ability, element) {
        var abilityInfo = abilities[ability.type]
        jQuery('.pgf-name', element).text(abilityInfo.name);
        element.addClass( 'ability-'+abilityInfo.type.toLowerCase() );

        if (ability.cooldown_end > turn.number) SetCooldown(ability.type);

        element.click(function(e){
            e.preventDefault();
            ActivateAbility(ability);
        });

        var tooltipContainer = jQuery('.pgf-tooltip-container', element);
        var tooltip = tooltipTemplate.clone().removeClass('pgf-hidden');
        tooltipContainer.html(RenderAbilityTootltip(tooltip, ability));
    }

    function RenderDeck() {
        pgf.base.RenderTemplateList(deckContainer, deck, RenderAbility, {});
    };

    function Refresh(event_data) {
        deck = event_data.angel.abilities;
        angelId = event_data.angel.id;
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


