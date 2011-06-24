
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

pgf.game.widgets.Heroes = function(selector, updater, widgets, params) {
    var instance = this;

    var content = jQuery(selector);
    var heroesContainer = jQuery('.pgf-heroes-list', content);
    var enemyContainer = jQuery('#pgf-enemy-widget');

    var data = {};

    function RenderMessagesLog(index, data, element) {
        jQuery('.pgf-message', element).text(data.text);
        jQuery('.pgf-message-pattern-id', element).text(data.pattern_id);
    }

    function RenderHero(index, data, element) {
        
        jQuery('.pgf-wisdom', element).text(data.base.wisdom);
        jQuery('.pgf-name', element).text(data.base.name);
        jQuery('.pgf-health', element).text(data.base.health);
        jQuery('.pgf-max-health', element).text(data.base.max_health);

        jQuery('.pgf-intellect', element).text(data.primary.intellect);
        jQuery('.pgf-constitution', element).text(data.primary.constitution);
        jQuery('.pgf-reflexes', element).text(data.primary.reflexes);
        jQuery('.pgf-chaoticity', element).text(data.primary.chaoticity);

        var lastAction = data.actions[data.actions.length-1];
        
        jQuery('.pgf-short-description', element).text(lastAction.short_description);

        var percents = lastAction.percents * 100;
        jQuery('.pgf-percents', element).text(percents.toFixed());

        jQuery('.pgf-entropy', element).text(lastAction.entropy);
        jQuery('.pgf-entropy-barier', element).text(lastAction.entropy_barier);

        var position = data.position;
        if (position.place) {
            jQuery('.pgf-position-type', element).text(position.place.type);
            jQuery('.pgf-position-name', element).text(position.place.name);
        }
        if (position.road) {
            jQuery('.pgf-position-type', element).text('road');
            jQuery('.pgf-position-name', element).text(position.road.point_1.name + ' - ' + position.road.point_2.name);
        }

        pgf.base.RenderTemplateList(jQuery('.pgf-messages-log', element), data.messages, RenderMessagesLog, {});

        // fill enemy window
        // TODO: move types into enume generated from python sources
        if (lastAction.type == 'BATTLE_PVE_1x1') {
            jQuery('.pgf-wisdom', enemyContainer).text(lastAction.data.npc.base.wisdom);
            jQuery('.pgf-name', enemyContainer).text(lastAction.data.npc.base.name);
            jQuery('.pgf-health', enemyContainer).text(lastAction.data.npc.base.health);
            jQuery('.pgf-max-health', enemyContainer).text(lastAction.data.npc.base.max_health);
            
            jQuery('.pgf-intellect', enemyContainer).text(lastAction.data.npc.primary.intellect);
            jQuery('.pgf-constitution', enemyContainer).text(lastAction.data.npc.primary.constitution);
            jQuery('.pgf-reflexes', enemyContainer).text(lastAction.data.npc.primary.reflexes);
            jQuery('.pgf-chaoticity', enemyContainer).text(lastAction.data.npc.primary.chaoticity);
        }
        else {
            jQuery('.pgf-wisdom', enemyContainer).text(0);
            jQuery('.pgf-name', enemyContainer).text('--------');
            jQuery('.pgf-health', enemyContainer).text(0);
            jQuery('.pgf-max-health', enemyContainer).text(0);
            
            jQuery('.pgf-intellect', enemyContainer).text(0);
            jQuery('.pgf-constitution', enemyContainer).text(0);
            jQuery('.pgf-reflexes', enemyContainer).text(0);
            jQuery('.pgf-chaoticity', enemyContainer).text(0);

        }
    }

    this.CurrentHero = function() {
        for (var hero_id in data) {
            return data[hero_id];
        }
        return null;
    };

    this.Refresh = function() {
        data = updater.data.data.heroes;
    };

    this.Render = function() {
        var heroes_list = [];
        for (var hero_id in data) {
            heroes_list.push(data[hero_id]);
        }
        pgf.base.RenderTemplateList(heroesContainer, heroes_list, RenderHero, {});
    };

    jQuery(document).bind(pgf.game.DATA_REFRESHED_EVENT, function(){
        instance.Refresh();
        instance.Render();
    });
};

pgf.game.widgets.Date = function(selector, updater, widgets, params) {
    var instance = this;

    var content = jQuery(selector);
    var dateContainer = jQuery('.pgf-date-content', content);

    var turnNumber = jQuery('.pgf-turn-number', dateContainer);

    var data = {};

    this.Refresh = function() {
        data = updater.data.data.turn;
    };

    this.Render = function() {
        turnNumber.text(data.number);
    };

    jQuery(document).bind(pgf.game.DATA_REFRESHED_EVENT, function(){
        instance.Refresh();
        instance.Render();
    });
};

pgf.game.widgets.Cards = function(selector, updater, widgets, params) {

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
        var activationUrl = info.activation_link;
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
                                                            {action: activationUrl,
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
            pgf.forms.Post({action: activationUrl,
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


pgf.game.widgets.GameTabs = function(selector, params) {

    var container = jQuery(selector);
    var head = jQuery('#pgf-game-tabs-head', selector);
    var body = jQuery('#pgf-game-tabs-body', selector);

    var instance = this;

    this.OpenTab = function(tabName) {
        pgf.tooltip.Hide();

        jQuery('.pgf-tab', body).toggleClass('pgf-hidden', true);
        jQuery('.pgf-tab-link', head).toggleClass('active', false);

        var tabId = '#pgf-' + tabName + '-tab';
        var linkId = '#pgf-' + tabName + '-link';

        var currentTab = jQuery(tabId, body);

        currentTab.toggleClass('pgf-hidden', false); 
        jQuery(linkId, head).toggleClass('active', true); 

        return currentTab;
    };

    jQuery('.pgf-tab-link', head).each(function(i, v) {
        var el = jQuery(v);
        var id = el.attr('id');
        var name = id.substr(4, id.length-4-5);
        
        el.click(function(e){
            e.preventDefault();
            instance.OpenTab(name);
        });
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