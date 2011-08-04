
if (!window.pgf) {
    pgf = {};
}

if (!pgf.game) {
    pgf.game = {};
}

if (!pgf.game.widgets) {
    pgf.game.widgets = {};
}

pgf.game.DATA_REFRESHED_EVENT = 'pgf-data-refreshed';

pgf.game.Updater = function(params) {

    var instance = this;
    var turnNumber = -1;

    this.data = {};

    this.Refresh = function() {
        
        jQuery.ajax({
            dataType: 'json',
            type: 'get',
            url: params.url,
            data: {turn_number: turnNumber}, 
            success: function(data, request, status) {

                instance.data = data;
                turnNumber = data.turn_number;

                jQuery(document).trigger(pgf.game.DATA_REFRESHED_EVENT);
            },
            error: function() {
            },
            complete: function() {
            }
        });
    };
};

pgf.game.widgets.Hero = function(selector, updater, widgets, params) {
    var instance = this;

    var content = jQuery(selector);

    var data = undefined;

    this.RenderHero = function(data, widget) {

        if (!data) {
            return;
        }

        jQuery('.pgf-wisdom', widget).text(data.base.wisdom);
        jQuery('.pgf-name', widget).text(data.base.name);
        jQuery('.pgf-health', widget).text(data.base.health);
        jQuery('.pgf-max-health', widget).text(data.base.max_health);

        pgf.base.UpdateStatsBar(jQuery('.pgf-health-bar', widget), data.base.max_health, data.base.health);

        jQuery('.pgf-intellect', widget).text(data.primary.intellect);
        jQuery('.pgf-constitution', widget).text(data.primary.constitution);
        jQuery('.pgf-reflexes', widget).text(data.primary.reflexes);
        jQuery('.pgf-chaoticity', widget).text(data.primary.chaoticity);
    };

    this.CurrentHero = function() {
        return data;
    };

    this.Refresh = function() {
        for (var hero_id in updater.data.data.heroes) {
            data = updater.data.data.heroes[hero_id];
            return;
        }
    };

    this.Render = function() {
        this.RenderHero(data, content);
    };

    jQuery(document).bind(pgf.game.DATA_REFRESHED_EVENT, function(){
        instance.Refresh();
        instance.Render();
    });
};

pgf.game.widgets.PlaceAndTime = function(selector, updater, widgets, params) {
    var instance = this;

    var content = jQuery(selector);

    var data = {};

    function RenderPosition(data, widget) {

        if (!data.position) {
            return;
        }
        
        if (data.position.place) {
            jQuery('.pgf-place .pgf-name', widget).text(data.position.place.name);
            jQuery('.pgf-place .pgf-comment', widget).text('TODO: add description for places here');
        }
    }

    function RenderTime(data, widget) {
        // 1 turn ~ 1 hour
        // 24 hours ~ 1 day
        // 30 days ~ month
        // 4 month ~ 1 year
        var months = ['Сухой месяц', 'Холодный месяц', 'Жаркий месяц', 'Сырой месяц']

        var turn = data.date.number;

        var year = Math.floor(turn / 24 /30 / 4);
        turn -= year * 24 * 30 * 4;

        var month = Math.floor( turn / 24 / 30);
        turn -= month * 24 * 30;

        var days = Math.floor( turn / 24);
        turn -= days * 24;

        var hours = turn;

        jQuery('.pgf-time .pgf-year', widget).text(1000 + year);
        jQuery('.pgf-time .pgf-month', widget).text(months[month]);
        jQuery('.pgf-time .pgf-day', widget).text(days);
        jQuery('.pgf-time .pgf-hours', widget).text(hours);
    }

    this.Refresh = function() {
        data.date = updater.data.data.turn;

        var hero = widgets.heroes.CurrentHero();
        if (hero) {
            data.position = hero.position;
        }
        else {
            data.position = undefined;
        }
    };

    this.Render = function() {
        RenderPosition(data, content);
        RenderTime(data, content);
    };

    jQuery(document).bind(pgf.game.DATA_REFRESHED_EVENT, function(){
        instance.Refresh();
        instance.Render();
    });
};

pgf.game.widgets.Actions = function(selector, updater, widgets, params) {
    var instance = this;

    var widget = jQuery(selector);
    var actionInfoContainer = jQuery('.pgf-action-info-container', widget);
    var questsLine = jQuery('.pgf-quests-line', widget);
    var noQuestsMsg = jQuery('.pgf-no-quests-message', widget);

    var data = {};

    var ACTION_TYPES = {
        BATTLE_PvE_1x1: 'BATTLE_PVE_1x1'
    };

    var instance = this;

    function RenderQuest(index, data, element) {
    }

    function RenderQuests() {
        questsLine.toggleClass('pgf-hidden', !(data.quests.length > 0) )
        noQuestsMsg.toggleClass('pgf-hidden', data.quests.length > 0 )
        if (data.quests.length > 0) {
            pgf.base.RenderTemplateList(questsLine, data.quests, RenderQuest, {});
        }
    }

    function RenderOtherAction(action) {
        var otherAction = jQuery('.pgf-action-other', actionInfoContainer);
        otherAction.toggleClass('pgf-hidden', false);
        jQuery('.pgf-name', otherAction).text(action.short_description);
    }

    function RenderBattlePvE_1x1Action(action) {
        battleAction = jQuery('.pgf-action-battle-pve-1x1', actionInfoContainer);
        battleAction.toggleClass('pgf-hidden', false);
        widgets.heroes.RenderHero(action.data.npc, battleAction);
    }

    function RenderActionInfo() {
        
        var action = instance.CurrentAction();

        if (!action) {
            return;
        }

        jQuery('.pgf-action-info', actionInfoContainer).toggleClass('pgf-hidden', true);

        switch (action.type) {
        case ACTION_TYPES.BATTLE_PvE_1x1: {
            RenderBattlePvE_1x1Action(action);
            break;
        }
        default: {
            RenderOtherAction(action);
            break;
        }
        }
        
    }

    function RenderActions() {

        var rowClasses = ['pgf-current', 'pgf-previouse', 'pgf-prev-previouse']
        var rowNumber = 0;
        for (var i=data.actions.length-1; i >= data.actions.length - 4; --i) {

            var recordElement = jQuery('.pgf-actions-progress .'+rowClasses[rowNumber], widget);

            if (i < 0) {
                jQuery('.pgf-name', recordElement).text('');
                jQuery('.pgf-percents', recordElement).text('');
                pgf.base.UpdateStatsBar(jQuery('.pgf-progress-bar', recordElement), 1, 0);
            }
            else {
                jQuery('.pgf-name', recordElement).text(data.actions[i].short_description);
                jQuery('.pgf-percents', recordElement).text( parseInt(data.actions[i].percents * 100));
                pgf.base.UpdateStatsBar(jQuery('.pgf-progress-bar', recordElement), 1, data.actions[i].percents);
            }

            ++rowNumber;
        }
    }

    this.Refresh = function() {

        var hero = widgets.heroes.CurrentHero();

        if (hero) {
            data.actions = hero.actions;
            data.quests = hero.quests;
        }
        else {
            data.actions = [];
            data.quests = [];
        }
    };

    this.Render = function() {
        RenderQuests();
        RenderActions();
        RenderActionInfo();
    };

    this.CurrentAction = function() {
        return data.actions[data.actions.length-1];
    };

    jQuery(document).bind(pgf.game.DATA_REFRESHED_EVENT, function(){
        instance.Refresh();
        instance.Render();
    });
};

pgf.game.widgets.Log = function(selector, updater, widgets, params) {
    var instance = this;

    var content = jQuery(selector);

    var messages = [];

    var shortLogContainer = jQuery('.pgf-log-list', content);

    function RenderMessage(index, data, element) {
        jQuery('.pgf-turn-number', element).text(data.turn);
        jQuery('.pgf-message', element).text(data.message);
    }

    function RenderLog(data, widget) {
        var shortLog = [];
        for (var i=messages.length-1; i>=0 && i>messages.length-4; --i) {
            shortLog.push(messages[i]);
        }
        shortLog.reverse();

        pgf.base.RenderTemplateList(shortLogContainer, shortLog, RenderMessage, {});
    }

    this.Refresh = function() {
        var turnNumber = updater.data.data.turn.number;

        var hero = widgets.heroes.CurrentHero();

        var turnMessages = [];
        if (hero) {
            turnMessages = hero.messages;
        }

        for (var i=0; i<turnMessages.length; ++i) {
            messages.push({turn: turnNumber, message: turnMessages[i].text});
        }
    };

    this.Render = function() {
        RenderLog();
    };

    jQuery(document).bind(pgf.game.DATA_REFRESHED_EVENT, function(){
        instance.Refresh();
        instance.Render();
    });
};

pgf.game.widgets.Cards = function(selector, updater, widgets, params) {
    var instance = this;

    var widget = jQuery(selector);
    var deckContainer = jQuery('.pgf-cards-list', widget);
    var activateCardWidget = jQuery('#activate-card-block');
    var activateCardFormBlock = jQuery('.pgf-activate-form', activateCardWidget);

    jQuery('.pgf-cancel', activateCardWidget).click(function(e){
        e.preventDefault();
        widgets.switcher.ShowJournalWidget();
    });

    var deck = {};
    var turn = {};

    function SetCooldown(cardId) {
        jQuery('.card-'+cardId, widget).toggleClass('cooldown', true);
    }

    function ActivateCard(card) {

        if (card.cooldown_end > turn.number) {
            return;
        }

        var currentHero = widgets.heroes.CurrentHero();

        var heroId = undefined;
        if (currentHero) {
            heroId = currentHero.id;
        }

        if (card.use_form) {

            widgets.switcher.ShowActivateCardWidget();

            function OnSuccessActivation(form, data) {
                card.cooldown_end = data.data.cooldown_end;
                if (card.cooldown_end) SetCooldown(card.id);

                widgets.switcher.ShowJournalWidget();

                updater.Refresh();
            }

            jQuery.ajax({
                type: 'get',
                url: card.form_link,
                success: function(data, request, status) {
                    activateCardFormBlock.html(data);

                    if (heroId !== undefined) {
                        jQuery('#hero_id', tab).val(heroId);
                    }

                    var activationForm = new pgf.forms.Form(jQuery('form', activateCardFormBlock),
                                                            {action: card.activation_link,
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
            pgf.forms.Post({action: card.activation_link,
                            data: ajax_data,
                            OnSuccess: function(data) {
                                card.cooldown_end = data.data.cooldown_end;
                                if (card.cooldown_end) SetCooldown(card.id);
                            }
                           });
        }
        
    }

    function RenderCard(index, card, element) {
        jQuery('.pgf-name', element).text(card.name);
        element.addClass( 'card-' + card.id + ' ' +card.type.toLowerCase() );

        if (card.cooldown_end > turn.number) SetCooldown(card.id);

        element.click(function(e){
            e.preventDefault();
            ActivateCard(card);
        });
    }

    function RenderDeck() {

        var cards = [];

        for (var cardIndex in deck) {
            cards.push(deck[cardIndex]);
        }
        
        pgf.base.RenderTemplateList(deckContainer, cards, RenderCard, {});
    };

    this.Refresh = function() {
        deck = updater.data.data.deck;
        turn = updater.data.data.turn;
    };

    this.Render = function() {
        RenderDeck();
    };

    jQuery(document).bind(pgf.game.DATA_REFRESHED_EVENT, function(){
        instance.Refresh();
        instance.Render();
    });
};

pgf.game.widgets.WidgetSwitcher = function(selector) {

    var widget = jQuery(selector);

    var logWidget = jQuery('#log-block');
    var journalWidget = jQuery('#journal-block');

    var activateCardWidget = jQuery('#activate-card-block');
    var activateCardWidgetFormBlock = jQuery('#activate-card-block .pgf-activate-form');
    var mapWidget = jQuery('#map-block');

    var instance = this;

    this.ShowActivateCardWidget = function() { 
        logWidget.toggleClass('pgf-hidden', true);
        journalWidget.toggleClass('pgf-hidden', true);
        mapWidget.toggleClass('pgf-hidden', true);

        activateCardWidget.toggleClass('pgf-hidden', false);

        activateCardWidgetFormBlock.html('');
    };

    this.ShowJournalWidget = function() { 
        logWidget.toggleClass('pgf-hidden', false);
        journalWidget.toggleClass('pgf-hidden', false);

        activateCardWidget.toggleClass('pgf-hidden', true);
        mapWidget.toggleClass('pgf-hidden', true);
    };

    this.ShowMapWidget = function() { 
        logWidget.toggleClass('pgf-hidden', false);
        mapWidget.toggleClass('pgf-hidden', false);

        journalWidget.toggleClass('pgf-hidden', true);
        activateCardWidget.toggleClass('pgf-hidden', true);
    };

    jQuery('.pgf-show-journal').click(function(e){
        e.preventDefault();
        instance.ShowJournalWidget();
    });

    jQuery('.pgf-show-map').click(function(e){
        e.preventDefault();
        instance.ShowMapWidget();
    });

};

pgf.game.widgets.CardsOld = function(selector, updater, widgets, params) {

    var instance = this;

    var content = jQuery(selector);
    var deckContainer = jQuery('.pgf-cards-list', content);
    var tooltipTemplate = jQuery(params.tooltipTemplate);

    var deck = {};
    var turn = {};

    function ActivateCard(e) {

        e.preventDefault();

        var link = jQuery(e.target);

        var cardEl = link.closest('.pgf-card-record');

        var info = deck[link.data('id')];

        if (info.cooldown_end > turn.number) {
            return;
        }

        var formUrl = info.form_link;
        var useForm = info.use_form;

        var currentHero = widgets.heroes.CurrentHero();
        var heroId = undefined;
        if (currentHero) {
            heroId = currentHero.id;
        }

        if (useForm) {

            var tab = widgets.tabs.OpenTab('tmp');

            function OnSuccessActivation(form, data) {
                info.cooldown_end = data.data.cooldown_end;
                if (info.cooldown_end) cardEl.toggleClass('cooldown', true);

                widgets.tabs.OpenTab('cards');
                updater.Refresh();
            }

            jQuery.ajax({
                type: 'get',
                url: formUrl,
                success: function(data, request, status) {
                    tab.html(data);

                    if (heroId !== undefined) {
                        jQuery('#hero_id', tab).val(heroId);
                    }

                    var activationForm = new pgf.forms.Form(jQuery('form', tab),
                                                            {action: card.activation_link,
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
                ajax_data.hero_id = heroId;
            }
            pgf.forms.Post({action: card.activation_link,
                            data: ajax_data,
                            OnSuccess: function(data) {
                                info.cooldown_end = data.data.cooldown_end;
                                if (info.cooldown_end) cardEl.toggleClass('cooldown', true);
                            }
                           });
        }

    };

    function RenderCard(index, data, element) {
        jQuery('.pgf-card-name', element).text(data.name);
        jQuery('.pgf-card-form-link', element)
            .data('id', data.id)
            .click(ActivateCard);

        element.toggleClass('pgf-tooltip-target');

        if (data.cooldown_end > turn.number) {
            element.toggleClass('cooldown', true);
        }

        function ShowTooltip() {
            var tooltip = tooltipTemplate.clone().removeClass('pgf-template');

            jQuery('.pgf-card-name', tooltip).text(data.name);
            jQuery('.pgf-card-description', tooltip).text(data.description);
            jQuery('.pgf-card-artistic', tooltip).text(data.artistic);
            jQuery('.pgf-card-available-after-value', tooltip).text(data.cooldown_end - turn.number);

            jQuery('.pgf-card-available-after', tooltip).toggleClass('pgf-hidden', data.cooldown_end - turn.number <= 0);

            return tooltip;
        }

        pgf.tooltip.Set(element, 'function', ShowTooltip);
    }

    this.Refresh = function() {
        deck = updater.data.data.deck;
        turn = updater.data.data.turn;
    };

    this.Render = function() {

        var cards = [];
        
        for (var cardIndex in deck) {
            cards.push(deck[cardIndex]);
        }
        
        pgf.base.RenderTemplateList(deckContainer, cards, RenderCard, {});
    };

    jQuery(document).bind(pgf.game.DATA_REFRESHED_EVENT, function(){
        instance.Refresh();
        instance.Render();
    });
};


pgf.game.widgets.MapManager = function(updater, widgets, params) {
    
    var mapObjectsLayer = params.mapObjectsLayer;

    var mapInfoUrl = params.infoSrc;

    var cityTemplate = params.templates.cityTemplate;
    var heroTemplate = params.templates.heroTemplate;

    var mapInfo = {};

    var cellSize = params.cellSize;

    var heroesData = [];

    var instance = this;

    function RenderCity(place) {
        var el = cityTemplate.clone().removeClass('pgf-template');
        jQuery('.pgf-place-name', el).text(place.name);
        jQuery('.pgf-place-size', el).text(place.size);
        return el;
    }

    function RenderHero(hero) {
        var el = heroTemplate.clone().removeClass('pgf-template');
        jQuery('.pgf-hero-name', el).text(hero.base.name);
        return el;
    }

    function Init() {

        jQuery.ajax({
            dataType: 'json',
            type: 'get',
            url: mapInfoUrl,
            success: function(data, request, status) {
                mapInfo = data.data;
                
                for (var placeId in mapInfo.places) {
                    var place = mapInfo.places[placeId];
                    var html = RenderCity(place);
                    
                    var data = {id: 'place-'+placeId,
                                centerX: cellSize * place.pos.x + cellSize / 2,
                                centerY: cellSize * place.pos.y + cellSize / 2,
                                deltaX: -5,
                                deltaY: -5,
                                domElement: html};
                    
                    mapObjectsLayer.UpdateObject(data);
                }
            },
            error: function() {
            },
            complete: function() {
            }
        });
    }

    this.Refresh = function() {
        heroesData = updater.data.data.heroes;
    };

    this.Render = function() {
        for (var heroId in heroesData) {
            var hero = heroesData[heroId];

            var html = RenderHero(hero);

            var place = hero.position.place;
            var road  = hero.position.road;

            var data = {};

            if (place) {
                data = {id: 'hero-'+heroId,
                        centerX: cellSize * place.pos.x + cellSize / 2,
                        centerY: cellSize * place.pos.y + cellSize / 2,
                        deltaX: -3,
                        deltaY: -3,
                        domElement: html};
            }
            else {
                var percents = hero.position.percents;
                var position = {x: 0, y: 0};
                if (hero.position.invert_direction) {
                    position.x = cellSize * (road.point_2.pos.x + (road.point_1.pos.x - road.point_2.pos.x) * percents) + cellSize / 2;
                    position.y = cellSize * (road.point_2.pos.y + (road.point_1.pos.y - road.point_2.pos.y) * percents) + cellSize / 2;
                }
                else {
                    position.x = cellSize * (road.point_1.pos.x + (road.point_2.pos.x - road.point_1.pos.x) * percents) + cellSize / 2;
                    position.y = cellSize * (road.point_1.pos.y + (road.point_2.pos.y - road.point_1.pos.y) * percents) + cellSize / 2;
                }
                data = {id: 'hero-'+heroId,
                        centerX: position.x,
                        centerY: position.y,
                        deltaX: -3,
                        deltaY: -3,
                        domElement: html};
            }

            mapObjectsLayer.UpdateObject(data);
        }        
    };

    jQuery(document).bind(pgf.game.DATA_REFRESHED_EVENT, function(){
        instance.Refresh();
        instance.Render();
    });

    Init();
}