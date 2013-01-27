
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

pgf.game.events.DATA_REFRESHED = 'pgf-data-refreshed';
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

                instance.data = data.data;
                turnNumber = data.turn_number;

                jQuery(document).trigger(pgf.game.events.DATA_REFRESHED, instance.data);
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

    var tooltipArgs = jQuery.extend(true, {}, pgf.base.popoverArgs, {title: function(){return jQuery('#pgf-might-tooltip').html();} });
    jQuery('.pgf-might-record', content).tooltip(tooltipArgs);

    this.RenderHero = function(data, widget) {

        if (!data) return;

        var heroPageUrl = pgf.urls['game:heroes:show'](data.id);

        jQuery('.pgf-level', widget).text(data.base.level);
        jQuery('.pgf-destiny-points', widget).text(data.base.destiny_points);
        jQuery('.pgf-name', widget).text(data.base.name);
        jQuery('.pgf-hero-page-link', widget).attr('href', heroPageUrl);
        jQuery('.pgf-free-destiny-points', widget).attr('href', heroPageUrl).toggleClass('pgf-hidden', !data.base.destiny_points);
        jQuery('.pgf-health', widget).text(data.base.health);
        jQuery('.pgf-max-health', widget).text(data.base.max_health);
        jQuery('.pgf-experience', widget).text(parseInt(data.base.experience));
        jQuery('.pgf-experience-to-level', widget).text(data.base.experience_to_level);

        jQuery('.pgf-race-gender').removeClass('pgf-hidden');
        jQuery('.pgf-gender', widget).text(data.base.gender);
        jQuery('.pgf-race', widget).text(data.base.race);

        jQuery('.pgf-health-percents', widget).width( (100 * data.base.health / data.base.max_health) + '%');
        jQuery('.pgf-experience-percents', widget).width( (100 * data.base.experience / data.base.experience_to_level) + '%');

        jQuery('.pgf-power', widget).text(data.secondary.power);
        jQuery('.pgf-money', widget).text(data.money);
        jQuery('.pgf-might', widget).text(data.might);
        jQuery('.pgf-might-crit-chance', widget).text(data.might_crit_chance);

        jQuery('.pgf-energy', content).text(data.energy.value);
        jQuery('.pgf-max-energy', content).text(data.energy.max);
        jQuery('.pgf-energy-percents', content).width( (100 * data.energy.value / data.energy.max) + '%');
    };

    this.CurrentHero = function() {
        return data;
    };

    this.Refresh = function(game_data) {
        if (params.dataMode == 'pve') {
            data = game_data.hero;
        }
        if (params.dataMode == 'pvp_account') {
            data = game_data.account.hero;
        }
        if (params.dataMode == 'pvp_enemy') {
            data = game_data.enemy.hero;
        }
    };

    this.Render = function() {
        this.RenderHero(data, content);
    };

    jQuery(document).bind(pgf.game.events.DATA_REFRESHED, function(e, game_data){
        instance.Refresh(game_data);
        instance.Render();
    });
};

pgf.game.widgets.Time = function(selector, updater, widgets, params) {
    var instance = this;

    var content = jQuery(selector);

    var gameDate = jQuery('.pgf-game-date', content);
    var gameTime = jQuery('.pgf-game-time', content);

    var data = {};

    function RenderTime(data, widget) {
        gameDate.text(data.date.verbose_date);
        gameTime.text(data.date.verbose_time);
    }

    this.Refresh = function(game_data) {
        data.date = game_data.turn;
    };

    this.Render = function() {
        RenderTime(data, content);
    };

    jQuery(document).bind(pgf.game.events.DATA_REFRESHED, function(e, game_data){
        instance.Refresh(game_data);
        instance.Render();
    });
};

////////////////////////////
// quests code

pgf.game.widgets._RenderActor = function(index, actor, element) {

    var nameElement = jQuery('.pgf-name', element);

    var data = actor[2];

    jQuery('.pgf-role', element).text(actor[0]);

    var popoverTitle = undefined;
    var popoverContent = undefined;

    if (actor[1] == pgf.game.constants.ACTOR_TYPE.PERSON) {
        nameElement.text(data.name);

        popoverTitle = 'персонаж';

        var place = widgets.mapManager.GetPlaceData(data.place_id);
        var race = pgf.game.constants.RACE_TO_STR[data.race];
        var gender = pgf.game.constants.GENDER_TO_STR[data.gender];
        var profeccion = pgf.game.constants.PERSON_TYPE_TO_STR[data.type];

        var content = jQuery('#pgf-popover-person').clone();
        jQuery('.pgf-place', content).text(place.name);
        jQuery('.pgf-race', content).text(race);
        jQuery('.pgf-gender', content).text(gender);
        jQuery('.pgf-type', content).text(profeccion);
        
        if (data.mastery_verbose) {
            jQuery('.pgf-mastery', content).text(data.mastery_verbose);            
        }

        popoverContent = content.html();
    }

    if (actor[1] == pgf.game.constants.ACTOR_TYPE.PLACE) {

        var place = widgets.mapManager.GetPlaceData(data.id);

        nameElement.text(place.name);

        popoverTitle = 'город';

        var content = jQuery('#pgf-popover-place').clone();
        jQuery('.pgf-size', content).text(place.size);
        popoverContent = content.html();
    }

    if (actor[1] == pgf.game.constants.ACTOR_TYPE.MONEY_SPENDING) {
        nameElement.text(data.goal);
        popoverTitle = 'цель накопления';
        var content = jQuery('#pgf-popover-money-spending').clone();
        jQuery('.pgf-description', content).text(data.description);
        popoverContent = content.html();
    }

    var popoverArgs = jQuery.extend(true, {}, pgf.base.popoverArgs, {title: popoverTitle,
                                                                     content: popoverContent});
    nameElement.toggleClass('pgf-has-popover', true).popover(popoverArgs);
};

pgf.game.widgets._RenderChoice = function (index, choice, element) {
    element.text(choice);
};

pgf.game.widgets._RenderQuest = function(index, quest, element) {
    jQuery('.pgf-quest-icon', element)
        .removeClass()
        .addClass('quest-icon pgf-quest-icon')
        .addClass(quest.quest_type);

    jQuery('.pgf-quest-description', element).text(quest.quest_text);
    jQuery('.pgf-quest-action-description', element).text(quest.action_text);

    var actorsElement = jQuery('.pgf-actors', element);

    if (quest.actors.length) {
        actorsElement.toggleClass('pgf-hidden', false);
        pgf.base.RenderTemplateList(actorsElement, quest.actors, pgf.game.widgets._RenderActor, {});
    }
    else {
        actorsElement.toggleClass('pgf-hidden', true);
    }

    if (quest.choices.length) {
        jQuery('.pgf-choices', element).removeClass('pgf-hidden');
        pgf.base.RenderTemplateList(jQuery('.pgf-choices-container', element), quest.choices, pgf.game.widgets._RenderChoice, {});
    }
};


pgf.game.widgets.Quest = function(selector, updater, widgets, params) {
    var instance = this;

    var widget = jQuery(selector);

    var questsBlock = jQuery('.pgf-current-quests-block', widget);

    var currentQuest = jQuery('.pgf-current-quest', widget);

    var choicesBlock = jQuery('.pgf-quest-choices', widget);
    var noChoicesMsg = jQuery('.pgf-no-choices', choicesBlock);
    var choicesMsg = jQuery('.pgf-choices-container', choicesBlock);
    var futureChoiceMsg = jQuery('.pgf-future-choice', choicesBlock);

    var data = {};

    function RenderQuests() {
        pgf.base.HideTooltips(widget);
        if (data.quests.line && data.quests.line.length > 0) {
            pgf.game.widgets._RenderQuest(0, data.quests.line[data.quests.line.length-1], currentQuest);
        }
        else {
            pgf.game.widgets._RenderQuest(0, {quest_type: 'no-quest',
                                              quest_text: 'бездельничает',
                                              action_text: 'имитирует бурную деятельность',
                                              actors: [],
                                              choices: []}, currentQuest);
        }
    }

    function RenderChoiceVariant(index, variant, element) {

        var variantLink = jQuery('.pgf-choice-link', element);
        variantLink.text(variant[1]);

        if (variant[0] == null) {
            element.addClass('disabled');
            return;
        }

        var url = pgf.urls['game:quests:choose'](data.quests.id, data.quests.choice_id, variant[0]);

        variantLink.click( function(e){
                               e.preventDefault();

                               jQuery.ajax({   dataType: 'json',
                                               type: 'post',
                                               url: url,
                                               success: function(data, request, status) {

                                                   if (data.status == 'error') {
                                                       if (data.error) {
                                                           pgf.ui.dialog.Error({ message: data.error });                                                           
                                                       }
                                                       else{
                                                           pgf.ui.dialog.Error({ message: data.errors });                                                               
                                                       }

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
    }

    function RenderChoices() {
        var choiceId = data.quests.choice_id;
        var futureChoice = data.quests.future_choice;

        noChoicesMsg.toggleClass('pgf-hidden', !!choiceId);
        choicesMsg.toggleClass('pgf-hidden', true);
        futureChoiceMsg.toggleClass('pgf-hidden', !futureChoice);

        if (choiceId) {
            if (futureChoice) {
                futureChoiceMsg.text(futureChoice);
            }
            else {
                pgf.base.RenderTemplateList(choicesMsg, data.quests.choice_variants, RenderChoiceVariant, {});
                choicesMsg.toggleClass('pgf-hidden', false);
            }
        }
    }

    this.Refresh = function(game_data) {

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

    jQuery(document).bind(pgf.game.events.DATA_REFRESHED, function(e, game_data){
        instance.Refresh(game_data);
        instance.Render();
    });
};

pgf.game.widgets.QuestsLine = function(selector, updater, widgets, params) {
    var instance = this;

    var widget = jQuery(selector);

    var questsContainer = jQuery('.pgf-quests-line-container', widget);
    var noQuestsMsg = jQuery('.pgf-no-quests-message', widget);
    var moneySpentInfo = jQuery('.pgf-money-spent-info', widget);

    var data = {};

    function RenderQuests() {
        pgf.base.HideTooltips(widget);

        noQuestsMsg.toggleClass('pgf-hidden', !!(data.quests.line && data.quests.line.length > 0) );
        questsContainer.toggleClass('pgf-hidden', !(data.quests.line && data.quests.line.length > 0) );

        if (data.quests.line && data.quests.line.length > 0) {
            pgf.base.RenderTemplateList(questsContainer, data.quests.line, pgf.game.widgets._RenderQuest, {});
        }
        else {
        }
    }

    function RenderMoneySpentInfo() {

        var hero = widgets.heroes.CurrentHero();

        moneySpentInfo.removeClass('pgf-hidden');

        var goalText = {'heal': 'лечение',
                        'useless': 'на себя',
                        'artifact': 'новая экипировка',
                        'sharpening': 'улучшение экипировки',
                        'impact': 'изменение влияния'}[hero.next_spending];

        descriptionText = {'heal': 'Собирает деньги, чтобы поправить здоровье, когда понадобится.',
                           'useless': 'Копит золото для не очень полезных но безусловно необходимых трат.',
                           'artifact': 'Планирует приобритение новой экипировки.',
                           'sharpening': 'Собирает на улучшение экипировки.',
                           'impact': 'Планирует накопить деньжат, чтобы повлиять на «запомнившегося» персонажа.'}[hero.next_spending];;

        var moneySpendData = {quest_type: 'next-spending',
                              quest_text:  'Накопить золото',
                              actors: [['цель', pgf.game.constants.ACTOR_TYPE.MONEY_SPENDING , {goal: goalText, description: descriptionText}]],
                              choices: []
                             };

        pgf.game.widgets._RenderQuest(0, moneySpendData, moneySpentInfo);
    }

    this.Refresh = function(game_data) {

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
        RenderMoneySpentInfo();
    };

    jQuery(document).bind(pgf.game.events.DATA_REFRESHED, function(e, game_data){
        instance.Refresh(game_data);
        instance.Render();
    });
};

pgf.game.widgets.Action = function(selector, updater, widgets, params) {
    var instance = this;

    var widget = jQuery(selector);

    var actionBlock = jQuery('.pgf-current-action-block', widget);
    var actionInfo = jQuery('.pgf-action-info', widget);

    var data = {};

    function RenderAction() {

        var action = data.action;

        if (!action) return;

        jQuery('.pgf-action-info', widget).text(action.description);
        jQuery('.pgf-action-percents', widget).width( (action.percents * 100) + '%');
    }

    this.Refresh = function(game_data) {

        data.actions = [];

        if (params.dataMode == 'pve') {
            if (game_data.hero) {
                data.action = game_data.hero.action;                            
            }
        }

        if (params.dataMode == 'pvp') {
            if (game_data.account.hero) {
                data.action = game_data.account.hero.action;                            
            }
        }
    };

    this.Render = function() {
        RenderAction();
    };

    this.GetCurrentAction = function() {
        return data.action;
    };

    jQuery(document).bind(pgf.game.events.DATA_REFRESHED, function(e, game_data){
        instance.Refresh(game_data);
        instance.Render();
    });
};


pgf.game.widgets.Bag = function(selector, updater, widgets, params) {
    var instance = this;

    var widget = jQuery(selector);

    var bagContainer = jQuery('.pgf-bag-container', widget);
    var tabButton = jQuery('.pgf-bag-tab-button');

    var data = {};

    function RenderItem(index, item, element) {
        jQuery('.pgf-name', element).text(item.name);
        jQuery('.pgf-power-container', element).toggleClass('pgf-hidden', !item.equipped);
        jQuery('.pgf-power', element).text(item.power);
        jQuery('.pgf-quest-item-marker', element).toggleClass('pgf-hidden', !item.quest);
    }

    function RenderItems() {
        var items = [];
        for (var uuid in data.bag) {
            items.push(data.bag[uuid]);
        }
        pgf.base.RenderTemplateList(bagContainer, items, RenderItem, {});
    }

    this.Refresh = function(game_data) {

        var hero = widgets.heroes.CurrentHero();

        if (hero) {
            data.bag = hero.bag;
            data.quest_items_count = hero.secondary.quest_items_count;
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
        jQuery('.pgf-special-items-count').text(data.quest_items_count);
        jQuery('.pgf-loot-items-count', tabButton).text(data.loot_items_count);
        jQuery('.pgf-max-bag-size', tabButton).text(data.max_bag_size);
        jQuery('.pgf-item-count-container', tabButton).removeClass('pgf-hidden');
        RenderItems();

        jQuery('[rel="tooltip"]', widget).tooltip(pgf.base.tooltipsArgs);
    };

    jQuery(document).bind(pgf.game.events.DATA_REFRESHED, function(e, game_data){
        instance.Refresh(game_data);
        instance.Render();
    });
};

pgf.game.widgets.Equipment = function(selector, updater, widgets, params) {
    var instance = this;

    var widget = jQuery(selector);

    var data = {};

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

    this.Refresh = function(game_data) {

        data = {};

        if (params.dataMode == 'pve') {
            if (game_data.hero) {
                data = game_data.hero.equipment;                            
            }
        }

        if (params.dataMode == 'pvp_account') {
            if (game_data.account.hero) {
                data = game_data.account.hero.equipment;                            
            }
        }

        if (params.dataMode == 'pvp_enemy') {
            if (game_data.account.hero) {
                data = game_data.enemy.hero.equipment;                            
            }
        }
    };

    this.Render = function() {
        RenderEquipment();
    };

    jQuery(document).bind(pgf.game.events.DATA_REFRESHED, function(e, game_data){
        instance.Refresh(game_data);
        instance.Render();
    });
};

pgf.game.widgets.Log = function(selector, updater, widgets, params) {
    var instance = this;

    var content = jQuery(selector);

    var messages = [];

    var shortLogContainer = jQuery('.pgf-log-list', content);

    function RenderDiaryMessage(index, message, element) {

        var text = "";
        for (var i in message[1]) {
            if (i == 0) {
                text += "<div class='submessage' style='vertical-align: top;'>" + message[1][i][2] + "</div>";                
            }
            else {
                text += "<div class='submessage'>" + message[1][i][2] + "</div>";
            }
        }

        jQuery('.pgf-time', element).text(message[1][0][3]);
        jQuery('.pgf-date', element).text(message[0]);
        jQuery('.pgf-message', element).html(text);
    }

    function RenderLogMessage(index, message, element) {
        jQuery('.pgf-time', element).text(message[0]);
        
        var text = "";
        for (var i in message[1]) {
            if (i == 0) {
                text += "<div class='submessage' style='vertical-align: top;'>" + message[1][i][2] + "</div>";                
            }
            else {
                text += "<br/><div class='submessage'>" + message[1][i][2] + "</div>";
            }
        }

        jQuery('.pgf-message', element).html(text);
    }

    function RenderLog(data, widget) {

        if (params.type == 'log') {
            pgf.base.RenderTemplateList(shortLogContainer, messages, RenderLogMessage, {});
        }
        if (params.type == 'diary') {
            pgf.base.RenderTemplateList(shortLogContainer, messages, RenderDiaryMessage, {});
        }

    }

    this.Refresh = function(game_data) {

        var heroData = undefined;

        if (params.dataMode == "pve") {
            heroData = game_data.hero;
        }

        if (params.dataMode == "pvp") {
            heroData = game_data.account.hero;
        }

        var turnMessages = [];
        if (heroData) {
            if (params.type == 'log') {
                turnMessages = heroData.messages;
            }
            if (params.type == 'diary') {
                turnMessages = heroData.diary;
            }
        }

        var lastTimestamp = -1;
        var lastGameTime = undefined;

        if (messages.length > 0)  messages.shift(); // if messages has elements, remove last since it can be not full

        if (messages.length > 0) lastTimestamp = messages[0][1][messages[0][1].length-1][0]; //get linux timestamp
        if (messages.length > 0) lastGameTime = messages[0][0]; //get game time
        
        for (var i=0; i<=turnMessages.length-1; ++i) {

            if (turnMessages[i][0] <= lastTimestamp) continue;

            if (lastGameTime == turnMessages[i][1]) {
                messages[0][1].push(turnMessages[i]);
            }
            else {
                messages.unshift([turnMessages[i][1], [turnMessages[i]]]);                    
            }

            lastGameTime = turnMessages[i][1];
        }

    };

    this.Render = function() {
        RenderLog();
    };

    jQuery(document).bind(pgf.game.events.DATA_REFRESHED, function(e, game_data){
        instance.Refresh(game_data);
        instance.Render();
    });
};
