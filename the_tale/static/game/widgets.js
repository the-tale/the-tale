
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

pgf.game.events.DATA_REFRESHED_EVENT = 'pgf-data-refreshed';
pgf.game.events.DATA_REFRESH_NEEDED = 'pgf-data-refresh-needed'

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

                jQuery(document).trigger(pgf.game.events.DATA_REFRESHED_EVENT);
            },
            error: function() {
            },
            complete: function() {
            }
        });
    };

    jQuery(document).bind(pgf.game.events.DATA_REFRESH_NEEDED, function(e){
        instance.Refresh();
    });
};

pgf.game.widgets.Hero = function(selector, updater, widgets, params) {
    var instance = this;

    var content = jQuery(selector);

    var data = undefined;

    this.RenderHero = function(data, widget) {

        if (!data) return;

        jQuery('.pgf-level', widget).text(data.base.level);
        jQuery('.pgf-destiny-points', widget).text(data.base.destiny_points);
        jQuery('.pgf-name', widget).text(data.base.name);
        jQuery('.pgf-hero-page-link', widget).attr('href', pgf.urls['game:heroes:'](data.id));
        jQuery('.pgf-health', widget).text(data.base.health);
        jQuery('.pgf-max-health', widget).text(data.base.max_health);
        jQuery('.pgf-experience', widget).text(data.base.experience);
        jQuery('.pgf-experience-to-level', widget).text(data.base.experience_to_level);

        pgf.base.UpdateStatsBar(jQuery('.pgf-health-bar', widget), data.base.max_health, data.base.health);
        pgf.base.UpdateStatsBar(jQuery('.pgf-experience-bar', widget), data.base.experience_to_level, data.base.experience);

        jQuery('.pgf-min-damage', widget).text(data.secondary.min_damage);
        jQuery('.pgf-max-damage', widget).text(data.secondary.max_damage);
        jQuery('.pgf-move-speed', widget).text(data.secondary.move_speed);
        jQuery('.pgf-battle-speed', widget).text(data.secondary.battle_speed);
        jQuery('.pgf-armor', widget).text(data.secondary.armor);

        jQuery('.pgf-money', widget).text(data.money);
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

    jQuery(document).bind(pgf.game.events.DATA_REFRESHED_EVENT, function(){
        instance.Refresh();
        instance.Render();
    });
};

pgf.game.widgets.Time = function(selector, updater, widgets, params) {
    var instance = this;

    var content = jQuery(selector);
    var timeIcon = jQuery('.pgf-time-icon', content);

    var data = {};

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

        timeIcon.removeClass('sunrise sunset midnight noon');
        if (4 < hours && hours <= 10) timeIcon.addClass('sunrise');
        if (10 < hours && hours <= 16) timeIcon.addClass('noon');
        if (16 < hours && hours <= 22) timeIcon.addClass('sunset');
        if (22 < hours || hours <= 4) timeIcon.addClass('midnight');
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
        RenderTime(data, content);
    };

    jQuery(document).bind(pgf.game.events.DATA_REFRESHED_EVENT, function(){
        instance.Refresh();
        instance.Render();
    });
};

pgf.game.widgets.Actions = function(selector, updater, widgets, params) {
    var instance = this;

    var widget = jQuery(selector);
    
    var actionBlock = jQuery('.pgf-current-action-block', widget);
    var questsBlock = jQuery('.pgf-current-quests-block', widget)

    var actionInfo = jQuery('.pgf-action-info', widget);
    var questsLine = jQuery('.pgf-quests-line', widget);
    var noQuestsMsg = jQuery('.pgf-no-quests-message', widget);

    var choicesBlock = jQuery('.pgf-quest-choices', widget);
    var noChoicesMsg = jQuery('.pgf-no-choices', choicesBlock);
    var choicesMsg = jQuery('.pgf-choices', choicesBlock);

    var data = {};

    var ACTION_TYPES = {
        IDLENESS: 'IDLENESS',
        BATTLE_PvE_1x1: 'BATTLE_PVE_1x1',
        QUEST: 'QUEST',
        MOVE_TO: 'MOVE_TO',
        RESURRECT: 'RESURRECT',
        IN_CITY: 'IN_CITY'
    };

    var instance = this;

    function RenderQuest(index, data, element) {
        jQuery('.pgf-quest-icon', element)
            .removeClass()
            .addClass('quest-icon pgf-quest-icon')
            .toggleClass('pgf-hidden', !data.quest_text)
            .addClass(data.quest_type)
            .data('tooltip', data.quest_text);

        jQuery('.pgf-action-icon', element)
            .removeClass()
            .addClass('action-icon pgf-action-icon')
            .toggleClass('pgf-hidden', !data.action_text)
            .addClass(data.action_type)
            .data('tooltip', data.action_text);
        
    }

    function RenderQuests() {
        questsLine.toggleClass('pgf-hidden', !(data.quests.line && data.quests.line.length > 0) )
        noQuestsMsg.toggleClass('pgf-hidden', !!(data.quests.line && data.quests.line.length > 0) )

        jQuery('.pgf-quests-progress', questsBlock).toggleClass('pgf-hidden', !(data.quests.line && data.quests.line.length > 0) )

        if (data.quests.line && data.quests.line.length > 0) {
            pgf.base.RenderTemplateList(questsLine, data.quests.line, RenderQuest, {});
        }
    }

    function RenderOtherAction(action) {
        var otherAction = jQuery('.pgf-action-other', actionInfo);
        otherAction.toggleClass('pgf-hidden', false);
        jQuery('.pgf-name', otherAction).text(action.short_description);
    }

    function RenderIdlenessAction(action) {
        var idlenessAction = jQuery('.pgf-action-idleness', actionInfo);
        idlenessAction.toggleClass('pgf-hidden', false);
    }

    function RenderQuestAction(action) {
        var questAction = jQuery('.pgf-action-quest', actionInfo);
        questAction.toggleClass('pgf-hidden', false);
    }

    function RenderMoveToAction(action) { 
        var moveToAction = jQuery('.pgf-action-move-to', actionInfo);
        var destinationId = action.specific.place_id;
        var placeName = widgets.mapManager.GetPlaceData(destinationId).name;
        jQuery('.pgf-place-name', moveToAction).text(placeName);
        moveToAction.toggleClass('pgf-hidden', false);
    }

    function RenderBattlePvE_1x1Action(action) {
        var battleAction = jQuery('.pgf-action-battle-pve-1x1', actionInfo);
        battleAction.toggleClass('pgf-hidden', false);
        jQuery('.pgf-mob-name', battleAction).text(action.specific.mob.name);
    }
    
    function RenderResurrectAction(action) {
        var resurrectAction = jQuery('.pgf-action-resurrect', actionInfo);
        resurrectAction.toggleClass('pgf-hidden', false);
    }

    function RenderInCityAction(action) {
        var inCityAction = jQuery('.pgf-action-in-city', actionInfo);
        var cityId = action.data.city;
        var placeName = widgets.mapManager.GetPlaceData(cityId).name;
        jQuery('.pgf-place-name', inCityAction).text(placeName);
        inCityAction.toggleClass('pgf-hidden', false);
    }

    function RenderActionInfo(action) {

        if (!action) return;

        jQuery('.pgf-action-info', actionInfo).toggleClass('pgf-hidden', true);

        switch (action.type) {
        case ACTION_TYPES.IDLENESS: {
            RenderIdlenessAction(action);
            break;
        }
        case ACTION_TYPES.QUEST: {
            RenderQuestAction(action);
            break;
        }
        case ACTION_TYPES.MOVE_TO: {
            RenderMoveToAction(action);
            break;
        }
        case ACTION_TYPES.BATTLE_PvE_1x1: {
            RenderBattlePvE_1x1Action(action);
            break;
        }
        case ACTION_TYPES.RESURRECT: {
            RenderResurrectAction(action);
            break;
        }
        case ACTION_TYPES.IN_CITY: {
            RenderInCityAction(action);
            break;
        }
        default: {
            RenderOtherAction(action);
            break;
        }
        }
        
    }

    function RenderAction() {
        
        var action = data.actions[data.actions.length-1];

        if (!action) return;

        jQuery('.pgf-name', actionBlock).text(action.short_description);
        jQuery('.pgf-percents', actionBlock).text( parseInt(action.percents * 100));
        pgf.base.UpdateStatsBar(jQuery('.pgf-progress-bar', actionBlock), 1, action.percents);
        
        RenderActionInfo(action);
    }

    function RenderChoices() {
        
        var questId = data.quests.id;
        var subquestId = data.quests.subquest_id;
        var choiceText = data.quests.choice_text;
        var choiceId = data.quests.choice_id;

        noChoicesMsg.toggleClass('pgf-hidden', !!choiceId);
        choicesMsg.toggleClass('pgf-hidden', !choiceId);

        if (choiceId) {
            choicesMsg.html(choiceText);
            jQuery('.pgf-choice', choicesMsg).each(function(i, v){
                var el = jQuery(v);
                
                var choice = el.data('choice');
                var url = pgf.urls['game:quests:choose'](questId, subquestId, choiceId, choice)
                el.click(function(e){
                    e.preventDefault();
                    
                    jQuery.ajax({
                        dataType: 'json',
                        type: 'post',
                        url: url,
                        success: function(data, request, status) {

                            if (data.status == 'error') {
                                pgf.ui.dialog.Error({ message: data.errors });
                                return;
                            }

                            if (data.status == 'ok') {
                                updater.Refresh();
                                return;
                            }

                            pgf.ui.dialog.Error({ message: 'unknown error while making choice' });

                        },
                        error: function() {
                        },
                        complete: function() {
                        }
                    });
                });
            });
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
        RenderAction();
        RenderActionInfo(instance.GetCurrentAction());
        RenderChoices();
    };

    this.GetCurrentAction = function() {
        return data.actions[data.actions.length-1];
    };

    this.GetAction = function(id) {
        if (id<0 || id>data.actions.length-1) return undefined;
        return data.actions[id];
    };

    jQuery(document).bind(pgf.game.events.DATA_REFRESHED_EVENT, function(){
        instance.Refresh();
        instance.Render();
    });
};

pgf.game.widgets.RenderItemTooltip = function(tooltip, data) {

    jQuery('.pgf-name', tooltip).text(data.name);
    jQuery('.pgf-type', tooltip).text(data.type);

    if (data.subtype) {
        jQuery('.pgf-subtype-enabled', tooltip).removeClass('pgf-hidden');
        jQuery('.pgf-subtype', tooltip).text(data.subtype);
    }

    for (var i in data.effects) {
        var effect = data.effects[i];

        switch(effect.type) {
        case 'WEAPON_BASE': {
            jQuery('.pgf-min-damage', tooltip).text(effect.min_damage);
            jQuery('.pgf-max-damage', tooltip).text(effect.max_damage);
            jQuery('.pgf-battle-speed', tooltip).text(effect.battle_speed);
            jQuery('.pgf-effect-weapon-base', tooltip).removeClass('pgf-hidden');
            break;
        }
        case 'ARMOR_BASE': {
            jQuery('.pgf-armor', tooltip).text(effect.armor);
            jQuery('.pgf-battle-speed', tooltip).text(effect.battle_speed);
            jQuery('.pgf-effect-armor-base', tooltip).removeClass('pgf-hidden');
            break;
        }
        }
    }

    return tooltip;
};


pgf.game.widgets.Bag = function(selector, updater, widgets, params) {
    var instance = this;

    var widget = jQuery(selector);
    
    var bagQuestsBlock = jQuery('.pgf-bag-quests');
    var bagBlock = jQuery('.pgf-bag');

    var bagQuestsContainer = jQuery('.pgf-bag-container', bagQuestsBlock);
    var bagContainer = jQuery('.pgf-bag-container', bagBlock);

    var tooltipTemplate = jQuery(params.tooltipTemplate);

    var data = {};

    var instance = this;

    function RenderItem(index, data, element) {
        jQuery('.pgf-name', element).text(data.name);
        jQuery('.pgf-cost', element).text(data.cost);

        var tooltipContainer = jQuery('.pgf-tooltip-container', element);
        var tooltip = tooltipTemplate.clone().removeClass('pgf-hidden');
        tooltipContainer.html(pgf.game.widgets.RenderItemTooltip(tooltip, data));
    }

    function RenderItems() {
        var quests = [];
        var items = [];
        for (var uuid in data.bag) {
            if (data.bag[uuid].quest) {
                quests.push(data.bag[uuid]);
            }
            else {
                items.push(data.bag[uuid]);
            }
        }
        bagQuestsBlock.toggleClass('pgf-hidden', quests.length==0)
        bagBlock.toggleClass('pgf-hidden', items.length==0)

        pgf.base.RenderTemplateList(bagContainer, items, RenderItem, {});
        pgf.base.RenderTemplateList(bagQuestsContainer, quests, RenderItem, {});
    }

    this.Refresh = function() {

        var hero = widgets.heroes.CurrentHero();

        if (hero) {
            data.bag = hero.bag;
            data.loot_items_count = hero.secondary.loot_items_count;
            data.max_bag_size = hero.secondary.max_bag_size;
        }
        else {
            data = { bag: {},
                     loot_items_count: 0,
                     max_bag_size: 0};
        }
    };

    this.Render = function() {
        jQuery('.pgf-loot-items-count', widget).text(data.loot_items_count);
        jQuery('.pgf-max-bag-size', widget).text(data.max_bag_size);
        RenderItems();
    };

    jQuery(document).bind(pgf.game.events.DATA_REFRESHED_EVENT, function(){
        instance.Refresh();
        instance.Render();
    });
};

pgf.game.widgets.Equipment = function(selector, updater, widgets, params) {
    var instance = this;

    var widget = jQuery(selector);

    var data = {};

    var instance = this;   
    
    var tooltipTemplate = jQuery(params.tooltipTemplate);

    function RenderArtifact(element, data) {
        element.text(data.name);
        var tooltipContainer = element.siblings('.pgf-tooltip-container');
        var tooltip = tooltipTemplate.clone().removeClass('pgf-hidden');
        tooltipContainer.html(pgf.game.widgets.RenderItemTooltip(tooltip, data));
    }

    function RenderEquipment() {
        for (var slot in data) {
            RenderArtifact(jQuery('.pgf-'+slot, selector), data[slot]);
        }
    }

    this.Refresh = function() {

        var hero = widgets.heroes.CurrentHero();

        if (hero) {
            data = hero.equipment;
        }
        else {
            data = {};
        }
    };

    this.Render = function() {
        RenderEquipment();
    };

    jQuery(document).bind(pgf.game.events.DATA_REFRESHED_EVENT, function(){
        instance.Refresh();
        instance.Render();
    });
};

pgf.game.widgets.Log = function(selector, updater, widgets, params) {
    var instance = this;

    var content = jQuery(selector);

    var messages = [];

    var VISIBLE_MESSAGES_NUMBER = 10;

    var shortLogContainer = jQuery('.pgf-log-list', content);

    function RenderMessage(index, data, element) {
        jQuery('.pgf-turn-number', element).text(data.turn);
        jQuery('.pgf-message', element).text(data.message);
    }

    function RenderLog(data, widget) {
        var shortLog = [];
        for (var i=messages.length-1; i>=0 && i>messages.length-1-VISIBLE_MESSAGES_NUMBER; --i) {
            shortLog.push(messages[i]);
        }
        // shortLog.reverse();

        pgf.base.RenderTemplateList(shortLogContainer, shortLog, RenderMessage, {});
    }

    this.Refresh = function() {
        var turnNumber = updater.data.data.turn.number;

        var hero = widgets.heroes.CurrentHero();

        var turnMessages = [];
        if (hero) {
            turnMessages = hero.messages;
        }

        messages = []

        for (var i=0; i<turnMessages.length; ++i) {
            messages.push({turn: turnNumber, message: turnMessages[i]});
        }
    };

    this.Render = function() {
        RenderLog();
    };

    jQuery(document).bind(pgf.game.events.DATA_REFRESHED_EVENT, function(){
        instance.Refresh();
        instance.Render();
    });
};

pgf.game.widgets.WidgetSwitcher = function() {

    var logWidget = jQuery('#log-block');

    var activateAbilityWidget = jQuery('#activate-ability-block');
    var activateAbilityWidgetFormBlock = jQuery('#activate-ability-block .pgf-activate-form');
    var mapWidget = jQuery('#map-block');

    var instance = this;

    this.ShowActivateAbilityWidget = function() { 
        logWidget.toggleClass('pgf-hidden', true);
        mapWidget.toggleClass('pgf-hidden', true);

        activateAbilityWidget.toggleClass('pgf-hidden', false);

        activateAbilityWidgetFormBlock.html('');
    };

    this.ShowMapWidget = function() { 
        logWidget.toggleClass('pgf-hidden', false);
        mapWidget.toggleClass('pgf-hidden', false);

        activateAbilityWidget.toggleClass('pgf-hidden', true);
    };
};