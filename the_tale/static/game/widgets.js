
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
pgf.game.events.DATA_REFRESH_NEEDED = 'pgf-data-refresh-needed';

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
        jQuery('.pgf-experience', widget).text(parseInt(data.base.experience));
        jQuery('.pgf-experience-to-level', widget).text(data.base.experience_to_level);

        jQuery('.pgf-health-percents', widget).width( (100 * data.base.health / data.base.max_health) + '%');
        jQuery('.pgf-experience-percents', widget).width( (100 * data.base.experience / data.base.experience_to_level) + '%');

        jQuery('.pgf-power', widget).text(data.secondary.power);
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
    };

    this.Render = function() {
        RenderTime(data, content);
    };

    jQuery(document).bind(pgf.game.events.DATA_REFRESHED_EVENT, function(){
        instance.Refresh();
        instance.Render();
    });
};

pgf.game.widgets.Quest = function(selector, updater, widgets, params) {
    var instance = this;

    var widget = jQuery(selector);
    
    var questsBlock = jQuery('.pgf-current-quests-block', widget);

    var currentQuest = jQuery('.pgf-current-quest', widget);
    var noQuestsMsg = jQuery('.pgf-no-quests-message', widget);

    var choicesBlock = jQuery('.pgf-quest-choices', widget);
    var noChoicesMsg = jQuery('.pgf-no-choices', choicesBlock);
    var choicesMsg = jQuery('.pgf-choices', choicesBlock);

    var data = {};

    function RenderQuest(quest, element) {
        jQuery('.pgf-quest-icon', element)
            .removeClass()
            .addClass('quest-icon pgf-quest-icon')
            .addClass(quest.quest_type);

        jQuery('.pgf-quest-description', element).text(quest.quest_text);
        jQuery('.pgf-quest-action-description', element).text(quest.action_text);        
    }

    function RenderQuests() {
        noQuestsMsg.toggleClass('pgf-hidden', !!(data.quests.line && data.quests.line.length > 0) );

        jQuery('.pgf-quests-progress', questsBlock).toggleClass('pgf-hidden', !(data.quests.line && data.quests.line.length > 0) );

        if (data.quests.line && data.quests.line.length > 0) {
            RenderQuest(data.quests.line[data.quests.line.length-1], currentQuest);
        }
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
                var url = pgf.urls['game:quests:choose'](questId, subquestId, choiceId, choice);
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
            data.quests = hero.quests;
        }
        else {
            data.quests = [];
        }
    };

    this.Render = function() {
        RenderQuests();
        RenderChoices();
    };

    jQuery(document).bind(pgf.game.events.DATA_REFRESHED_EVENT, function(){
        instance.Refresh();
        instance.Render();
    });
};

pgf.game.widgets.QuestsLine = function(selector, updater, widgets, params) {
    var instance = this;

    var widget = jQuery(selector);
    
    var questsContainer = jQuery('.pgf-quests-line-container', widget);
    var noQuestsMsg = jQuery('.pgf-no-quests-message', widget);

    var data = {};

    function RenderQuest(index, quest, element) {
        jQuery('.pgf-quest-icon', element)
            .removeClass()
            .addClass('quest-icon pgf-quest-icon')
            .addClass(quest.quest_type);

        jQuery('.pgf-quest-description', element).text(quest.quest_text);
    }

    function RenderQuests() {
        noQuestsMsg.toggleClass('pgf-hidden', !!(data.quests.line && data.quests.line.length > 0) );

        if (data.quests.line && data.quests.line.length > 0) {
            pgf.base.RenderTemplateList(questsContainer, data.quests.line, RenderQuest, {});
        }
    }

    this.Refresh = function() {

        var hero = widgets.heroes.CurrentHero();

        if (hero) {
            data.quests = hero.quests;
        }
        else {
            data.quests = [];
        }
    };

    this.Render = function() {
        RenderQuests();
    };

    jQuery(document).bind(pgf.game.events.DATA_REFRESHED_EVENT, function(){
        instance.Refresh();
        instance.Render();
    });
};

pgf.game.widgets.Action = function(selector, updater, widgets, params) {
    var instance = this;

    var widget = jQuery(selector);
    
    var actionBlock = jQuery('.pgf-current-action-block', widget);
    var actionInfo = jQuery('.pgf-action-info', widget);

    var data = {};

    var ACTION_TYPES = {
        IDLENESS: 'IDLENESS',
        BATTLE_PvE_1x1: 'BATTLE_PVE1x1',
        QUEST: 'QUEST',
        MOVE_TO: 'MOVE_TO',
        RESURRECT: 'RESURRECT',
        IN_CITY: 'IN_CITY'
    };

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

        jQuery('.pgf-action-percents', widget).width( (action.percents * 100) + '%');
        
        RenderActionInfo(action);
    }

    this.Refresh = function() {

        var hero = widgets.heroes.CurrentHero();

        if (hero) {
            data.actions = hero.actions;
        }
        else {
            data.actions = [];
        }
    };

    this.Render = function() {
        RenderAction();
        RenderActionInfo(instance.GetCurrentAction());
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


pgf.game.widgets.Bag = function(selector, updater, widgets, params) {
    var instance = this;

    var widget = jQuery(selector);
    
    var bagContainer = jQuery('.pgf-bag-container', widget);

    var data = {};

    function RenderItem(index, data, element) {
        jQuery('.pgf-name', element).text(data.name);
        jQuery('.pgf-power-container', element).toggleClass('pgf-hidden', !data.equipped);
        jQuery('.pgf-power', element).text(data.power);
    }

    function RenderItems() {
        var items = [];
        for (var uuid in data.bag) {
            items.push(data.bag[uuid]);
        }
        pgf.base.RenderTemplateList(bagContainer, items, RenderItem, {});
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
    
    function RenderArtifact(element, data) {
        jQuery('.pgf-name', element).text(data.name);
        jQuery('.pgf-power', element).text(data.power);
        jQuery('.pgf-power-container', element).toggleClass('pgf-hidden', false);
    }

    function RenderEquipment() {
        jQuery('.pgf-power-container', selector).toggleClass('pgf-hidden', true);
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
            turnMessages = hero[params.messagesAttribute];
        }

        messages = [];

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