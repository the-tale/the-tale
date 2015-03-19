
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
pgf.game.events.GAME_DATA_SHOWED =  'pgf-game-data-showed';

pgf.game.Updater = function(params) {

    var INITIAL_REFRESH_DELAY = 1000;

    var instance = this;
    var refreshInterval = undefined;
    var refreshTimer = undefined;
    var refreshDelay = INITIAL_REFRESH_DELAY;

    var autoRefreshStopped = false;

    var oldDatas = {}; // turn_number: data
    var currentTurn = undefined;


    instance.data = {};

    instance.SetRefreshInterval = function(intervalTime) {
        refreshInterval = intervalTime;
        refreshTimer = setInterval(function(e){
            instance.Refresh();
        }, refreshInterval );
        autoRefreshStopped = false;
    };

    instance.StopAutoRefresh = function() {
        if (!refreshInterval) return;

        clearInterval(refreshTimer);
        autoRefreshStopped = true;
    };

    instance.ApplyNewData = function(newData) {

        currentTurn = newData.turn.number;

        // apply patch for hero if received data is patch
        if (newData.account && newData.account.hero.patch_turn != null) {
            var oldData = oldDatas[newData.account.hero.patch_turn];

            if (!oldData) return false;

            for (var field in oldData.account.hero) {
                if (field in newData.account.hero) continue;
                newData.account.hero[field] = oldData.account.hero[field];
            }
        }

        // apply patch for enemy if received data is patch
        if (newData.enemy && newData.enemy.hero.patch_turn != null) {
            var oldData = oldDatas[newData.enemy.hero.patch_turn];

            if (!oldData) return false;

            for (var field in oldData.enemy.hero) {
                if (field in newData.enemy.hero) continue;
                newData.enemy.hero[field] = oldData.enemy.hero[field];
            }
        }

        instance.data = newData;

        oldDatas[currentTurn] = newData;

        // remove old turns data
        var turns = [];
        for (var turnNumber in oldDatas) {
            turns.push(turnNumber);
        }
        turns.sort();
        for (var i=0; i<turns.length-2; ++i) {
            delete oldDatas[turns[i]];
        }

        return true;
    };

    instance.Refresh = function(fullRequest) {

        var url = params.url;

        if (!fullRequest && !jQuery.isEmptyObject(oldDatas)) {
            var clientTurns = [];
            for (var turnNumber in oldDatas) {
                clientTurns.push(turnNumber);
            }
            clientTurns = clientTurns.join()

            if (url.indexOf('?') != -1) {url += '&client_turns=' + clientTurns;}
            else {url += '?client_turns=' + clientTurns;}
        }

        jQuery.ajax({
            dataType: 'json',
            type: 'get',
            url: url,
            success: function(data, request, status) {

                if (data && data.data && data.data.account && data.data.account.is_old && data.data.account.is_own) {

                    setTimeout(function(e){
                        refreshDelay *= 1.618; //the golden ratio
                        instance.StopAutoRefresh();
                        instance.Refresh();
                    }, refreshDelay);
                    return;
                }

                refreshDelay = INITIAL_REFRESH_DELAY;

                if (autoRefreshStopped) {
                    instance.SetRefreshInterval(refreshInterval);
                }

                if (!instance.ApplyNewData(data.data)) {
                    instance.Refresh(true);
                    return;
                }

                jQuery(document).trigger(pgf.game.events.DATA_REFRESHED, instance.data);

                setTimeout(function(e){
                    jQuery('.pgf-wait-data').toggleClass('pgf-hidden', true);

                    if (jQuery('.pgf-game-data').hasClass('pgf-hidden')) {
                        jQuery('.pgf-game-data').toggleClass('pgf-hidden', false);
                        jQuery(document).trigger(pgf.game.map.events.MAP_RESIZED);
                        jQuery(document).trigger(pgf.game.events.GAME_DATA_SHOWED);
                    }
                }, 750);
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

    var tooltipArgs = jQuery.extend(true, {}, pgf.base.tooltipsArgs, {title: function(){return jQuery('.pgf-might-tooltip', content).html();},
                                                                      placement: "bottom"});
    jQuery('.pgf-might-record', content).tooltip(tooltipArgs);

    this.RenderHero = function(data, widget) {

        if (!data) return;

        var heroPageUrl = pgf.urls['game:heroes:show'](data.id);

        jQuery('.pgf-level', widget).text(data.base.level);
        jQuery('.pgf-destiny-points', widget).text(data.base.destiny_points);
        jQuery('.pgf-name', widget).text(data.base.name);
        jQuery('.pgf-hero-page-link', widget).attr('href', heroPageUrl);
        jQuery('.pgf-free-destiny-points', widget).attr('href', heroPageUrl).toggleClass('pgf-hidden', !data.base.destiny_points);

        jQuery('.pgf-health', widget).text(parseInt(data.base.health));
        jQuery('.pgf-max-health', widget).text(data.base.max_health);

        jQuery('.pgf-diary-block-health').text(parseInt(data.base.health));
        jQuery('.pgf-diary-block-max-health').text(data.base.max_health);

        jQuery('.pgf-experience', widget).text(parseInt(data.base.experience));
        jQuery('.pgf-experience-to-level', widget).text(data.base.experience_to_level);

        jQuery('.pgf-diary-block-experience').text(parseInt(data.base.experience));
        jQuery('.pgf-diary-block-experience-to-level').text(data.base.experience_to_level);

        jQuery('.pgf-race-gender').removeClass('pgf-hidden');
        jQuery('.pgf-gender', widget).text(pgf.game.constants.GENDER_TO_TEXT[data.base.gender]);
        jQuery('.pgf-race', widget).text(pgf.game.constants.RACE_TO_TEXT[data.base.race]);

        jQuery('.pgf-health-percents', widget).width( (100 * data.base.health / data.base.max_health) + '%');
        jQuery('.pgf-experience-percents', widget).width( (100 * data.base.experience / data.base.experience_to_level) + '%');

        jQuery('.pgf-physic-power', widget).text(data.secondary.power[0]);
        jQuery('.pgf-magic-power', widget).text(data.secondary.power[1]);
        jQuery('.pgf-money', widget).text(parseInt(data.base.money));
        jQuery('.pgf-might', widget).text(Math.round(data.might.value*100)/100);
        jQuery('.pgf-might-crit-chance', widget).text(Math.round(data.might.crit_chance*10000)/100.0);
        jQuery('.pgf-might-pvp-effectiveness-bonus', widget).text(Math.round(data.might.pvp_effectiveness_bonus*10000)/100.0);

        jQuery('.pgf-energy', content).text(data.energy.value);
        jQuery('.pgf-max-energy', content).text(data.energy.max);
        jQuery('.pgf-energy-bonus', content).text(data.energy.bonus);
        jQuery('.pgf-energy-percents', content).width( (100 * data.energy.value / data.energy.max) + '%');

        jQuery('.pgf-diary-block-energy').text(data.energy.value);
        jQuery('.pgf-diary-block-max-energy').text(data.energy.max);
        jQuery('.pgf-diary-block-energy-bonus').text(data.energy.bonus);

        // companion data
        jQuery('.pgf-companion', widget).toggleClass('pgf-hidden', !!(data.companion == null));
        jQuery('.pgf-no-companion', widget).toggleClass('pgf-hidden', !(data.companion == null));

        if (data.companion) {
            jQuery('.pgf-companion-info-link', widget).data('companion-id', data.companion.type);

            jQuery('.pgf-companion .pgf-name', widget).text(data.companion.name);
            jQuery('.pgf-companion .pgf-coherence', widget).text(data.companion.coherence);
            jQuery('.pgf-companion .pgf-real-coherence', widget).text(data.companion.real_coherence);
            jQuery('.pgf-companion .pgf-real-coherence-block', widget).toggleClass('pgf-hidden', data.companion.real_coherence == data.companion.coherence);

            jQuery('.pgf-companion .pgf-health', widget).text(parseInt(data.companion.health));
            jQuery('.pgf-companion .pgf-max-health', widget).text(data.companion.max_health);

            jQuery('.pgf-companion .pgf-experience', widget).text(parseInt(data.companion.experience));
            jQuery('.pgf-companion .pgf-experience-to-level', widget).text(data.companion.experience_to_level);

            jQuery('.pgf-companion .pgf-health-percents', widget).width( (100 * data.companion.health / data.companion.max_health) + '%');
            jQuery('.pgf-companion .pgf-experience-percents', widget).width( (100 * data.companion.experience / data.companion.experience_to_level) + '%');
        }
    };

    this.CurrentHero = function() {
        return data;
    };

    this.Refresh = function(game_data) {
        data = game_data.account.hero;
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

        popoverTitle = 'Горожанин';

        var place = widgets.mapManager.GetPlaceData(data.place);
        var race = pgf.game.constants.RACE_TO_TEXT[data.race];
        var gender = pgf.game.constants.GENDER_TO_TEXT[data.gender];
        var profession = pgf.game.constants.PERSON_TYPE_TO_TEXT[data.profession];

        var content = jQuery('#pgf-popover-person').clone();
        if (place) jQuery('.pgf-place', content).text(place.name);
        jQuery('.pgf-race', content).text(race);
        jQuery('.pgf-gender', content).text(gender);
        jQuery('.pgf-type', content).text(profession);

        if (data.mastery_verbose) {
            jQuery('.pgf-mastery', content).text(data.mastery_verbose);
        }

        nameElement.click(function(e){
            e.preventDefault();
            widgets.map.CenterOnPlace(place.id);
        });
    }

    if (actor[1] == pgf.game.constants.ACTOR_TYPE.PLACE) {

        var place = widgets.mapManager.GetPlaceData(data.id);

        if (place) nameElement.text(place.name);

        popoverTitle = 'город';

        var content = jQuery('#pgf-popover-place').clone();

        if (place) jQuery('.pgf-size', content).text(place.size);

        nameElement.click(function(e){
            e.preventDefault();
            widgets.map.CenterOnPlace(place.id);
        });
    }

    if (actor[1] == pgf.game.constants.ACTOR_TYPE.MONEY_SPENDING) {
        nameElement.text(data.goal);
        popoverTitle = 'цель накопления';
        var content = jQuery('#pgf-popover-money-spending').clone();
        jQuery('.pgf-description', content).text(data.description);

        nameElement.click(function(e){
            e.preventDefault();
        });
    }

    content.children(':first').toggleClass('pgf-actor-tooltip', true);
    popoverContent = content.html();

    var popoverArgs = jQuery.extend(true, {}, pgf.base.popoverArgs, {title: popoverTitle,
                                                                     placement: pgf.base.HorizTooltipPlacement,
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
        .addClass(quest.type);

    jQuery('.pgf-quest-description', element).text(quest.name);

    jQuery('.pgf-quest-rewards', element).toggleClass('pgf-hidden', !(quest.experience || quest.power));
    jQuery('.pgf-experience', element).text(quest.experience);
    jQuery('.pgf-power', element).text(quest.power);

    jQuery('.pgf-quest-action-description', element).text(quest.action);

    var actorsElement = jQuery('.pgf-actors', element);

    if (quest.actors && quest.actors.length) {
        actorsElement.toggleClass('pgf-hidden', false);
        pgf.base.RenderTemplateList(actorsElement, quest.actors, pgf.game.widgets._RenderActor, {});
    }
    else {
        actorsElement.toggleClass('pgf-hidden', true);
    }

    if (quest.choice) {
        jQuery('.pgf-choices', element).removeClass('pgf-hidden');
        pgf.base.RenderTemplateList(jQuery('.pgf-choices-container', element), [quest.choice], pgf.game.widgets._RenderChoice, {});
    }
    else {
        jQuery('.pgf-no-choices', element).removeClass('pgf-hidden');
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
        pgf.base.HideTooltips(widget, 'pgf-actor-tooltip');

        if (data.quests.length == 0) {
            pgf.game.widgets._RenderQuest(0, [], currentQuest);
            return;
        }

        var quest = data.quests.quests[data.quests.quests.length - 1];
        pgf.game.widgets._RenderQuest(0, quest.line[quest.line.length-1], currentQuest);
    }

    function RenderChoiceVariant(index, variant, element) {

        var variantLink = jQuery('.pgf-choice-link', element);
        variantLink.text(' ' + variant[1]);

        if (variant[0] == null) {
            variantLink.addClass('disabled');
            var tooltipArgs = jQuery.extend(true, {}, pgf.base.tooltipArgs, {title: 'выбор недоступен из-за характера героя',
                                                                             placement: pgf.base.HorizTooltipPlacement});
            variantLink.tooltip(tooltipArgs);
            return;
        }

        variantLink.click( function(e){
                               pgf.base.ToggleWait(variantLink, true);
                               variantLink.toggleClass('disabled', true);

                               e.preventDefault();

                               pgf.forms.Post({action: params.chooseUrl + '&option_uid=' + encodeURIComponent(variant[0]),
                                               data: {},
                                               wait: false,
                                               OnSuccess: function(data) {
                                                   updater.Refresh();
                                                   // no need to enable choices or disable spinner
                                                   // after refresh they will be redrawed

                                               },
                                               OnError: function(data) {RenderChoices();}
                                              });
                           });
    }

    function RenderChoices() {
        if (data.quests.length == 0 || data.quests.quests.length == 0) {
            return;
        }

        var quest = data.quests.quests[data.quests.quests.length - 1];
        var info = quest.line[quest.line.length-1];
        var futureChoice = info.choice;

        noChoicesMsg.toggleClass('pgf-hidden', !!futureChoice);
        choicesMsg.toggleClass('pgf-hidden', info.choice_alternatives.length == 0);
        futureChoiceMsg.toggleClass('pgf-hidden', !futureChoice);

        futureChoiceMsg.text(futureChoice);
        pgf.base.RenderTemplateList(choicesMsg, info.choice_alternatives, RenderChoiceVariant, {});
    }

    this.Refresh = function(game_data) {

        var hero = widgets.heroes.CurrentHero();
        var newQuests = [];

        if (hero) {
            newQuests = hero.quests;
        }

        if (!pgf.base.CompareObjects(data.quests, newQuests)) {
            data.quests = newQuests;
            return true;
        }

        return false;
    };

    this.Render = function() {
        RenderQuests();
        RenderChoices();
    };

    var MAP_LOADED = false;
    var QUEST_LOADED = false;

    jQuery(document).bind(pgf.game.events.DATA_REFRESHED, function(e, game_data){
        QUEST_LOADED = true;
        if (instance.Refresh(game_data)) {
            instance.Render();
        }
    });

    jQuery(document).bind(pgf.game.map.events.DATA_UPDATED, function() {
        if (MAP_LOADED) return;
        MAP_LOADED = true;
        if (!QUEST_LOADED) return;
        instance.Render();
    });
};

pgf.game.widgets.QuestsLine = function(selector, updater, widgets, params) {
    var instance = this;

    var widget = jQuery(selector);

    var questsContainer = jQuery('.pgf-quests-container', widget);
    var noQuestsMsg = jQuery('.pgf-no-quests-message', widget);
    var moneySpentInfo = jQuery('.pgf-money-spent-info', widget);

    var data = {};

    function RenderQuestsLine(index, quest, element) {
        pgf.base.RenderTemplateList(element, quest.line, pgf.game.widgets._RenderQuest, {});
    }

    function RenderQuests() {
        pgf.base.HideTooltips(widget, 'pgf-actor-tooltip');
        pgf.base.RenderTemplateList(questsContainer, data.quests.quests, RenderQuestsLine, {});
    }

    this.Refresh = function(game_data) {

        var hero = widgets.heroes.CurrentHero();
        var newQuests = [];

        if (hero) {
            newQuests = hero.quests;
        }

        var dataChanged = false;

        if (!pgf.base.CompareObjects(data.quests, newQuests)) {
            dataChanged = true;
        }

        data.quests = newQuests;

        return dataChanged;
    };

    this.Render = function() {
        RenderQuests();
    };

    var MAP_LOADED = false;
    var QUEST_LOADED = false;

    jQuery(document).bind(pgf.game.events.DATA_REFRESHED, function(e, game_data){
        QUEST_LOADED = true;
        if (instance.Refresh(game_data)) {
            instance.Render();
        }
    });

    jQuery(document).bind(pgf.game.map.events.DATA_UPDATED, function() {
        if (MAP_LOADED) return;
        MAP_LOADED = true;
        if (!QUEST_LOADED) return;
        instance.Render();
    });
};

pgf.game.widgets.CreateCardTooltip = function (data, cssClass) {
    var rarityClass = pgf.game.constants.CARD_RARITY[data.rarity].name.toLowerCase()+'-card-label';
    var rarityName = pgf.game.constants.CARD_RARITY[data.rarity].text;
    var description = pgf.game.constants.CARD_TYPE[data.type].description;

    var tooltip = '<ul class="unstyled '+cssClass+'" style="text-align: left;">';
    tooltip += '<li><h4>'+data.name+'</h4></li>';
    tooltip += '<li class="'+rarityClass+'">'+rarityName+'</li>';
    tooltip += '<li>'+description+'</li>';

    if (data.auction) {
        tooltip += '<hr/>';
        tooltip += '<li><i>может быть продана на рынке</i></li>';
    }
    tooltip += '</ul>';
    return tooltip;
};

pgf.game.widgets.Action = function(selector, updater, widgets, params) {
    var instance = this;

    var widget = jQuery(selector);

    var actionBlock = jQuery('.pgf-current-action-block', widget);
    var actionInfo = jQuery('.pgf-action-info', widget);

    var cardsListContainer = jQuery('.pgf-cards-container', widget)

    var data = {};

    instance.GetCards = function() {
        return data.cards;
    };

    function RenderAction() {

        var action = data.action;

        if (!action) return;

        jQuery('.pgf-action-info', widget).text(action.description);
        jQuery('.pgf-action-percents', widget).width( (action.percents * 100) + '%');

        jQuery('.pgf-boss-mark', widget).toggleClass('pgf-hidden', !action.is_boss);

        jQuery('.pgf-action-info-link', widget)
            .toggleClass('pgf-hidden', !action.info_link)
            .attr('href', action.info_link);
    }

    function RenderCards() {
        jQuery('.pgf-helps-count-to-new-card', widget).text(data.cardsHelpCount);
        jQuery('.pgf-new-card-progress', widget).width((data.cardsHelpCount / data.cardsHelpBarrier)*100+'%');

        jQuery('.pgf-cards-choices .pgf-card', widget).toggleClass('pgf-hidden', true);
        jQuery('.pgf-cards-choices .pgf-no-cards', widget).toggleClass('pgf-hidden', !jQuery.isEmptyObject(data.cards));

        jQuery('.pgf-new-card-icon', widget).toggleClass('pgf-hidden', data.cardsHelpCount < data.cardsHelpBarrier)
        jQuery('.pgf-get-card-statistics', widget).toggleClass('pgf-hidden', data.cardsHelpCount >= data.cardsHelpBarrier);
        jQuery('.pgf-get-card-button', widget).toggleClass('pgf-hidden', data.cardsHelpCount < data.cardsHelpBarrier);

        instance.ShowCards(cardsListContainer);

        jQuery('.pgf-combine-card-button', widget).toggleClass('pgf-hidden', data.cards.length < 2);
    }

    this.ShowCards = function(container, filterUIDs) {
        var cards = [];

        if (filterUIDs != undefined) {
            for (var i in data.cards) {
                if (filterUIDs.indexOf(data.cards[i].uid) != -1) {
                    cards.push(data.cards[i]);
                }
            };
        }
        else {
            cards = data.cards;
        }

        pgf.base.RenderTemplateList(container, cards, RenderCard, {});
    };

    var cardTooltipArgs = jQuery.extend({}, pgf.base.tooltipsArgs);
    cardTooltipArgs.placement = function(tip, element) {
        var offset = jQuery(element).offset();
        if (offset.left == 0 && offset.top == 0) {
            jQuery(tip).addClass('pgf-hidden');
        }
        return 'right';
    }

    function RenderCard(index, item, element) {
        jQuery('.pgf-card-record', element)
            .text(item.name)
            .addClass(pgf.game.constants.CARD_RARITY[item.rarity].name.toLowerCase()+'-card-label')
            .data('card-uid', item.uid)
            .addClass('pgf-card-uid-'+item.uid);

        var tooltipClass = 'pgf-card-tooltip';
        var tooltip = pgf.game.widgets.CreateCardTooltip(item, tooltipClass);
        pgf.game.widgets.UpdateElementTooltip(element, tooltip, tooltipClass, cardTooltipArgs);
    }

    this.Refresh = function(game_data) {

        var newData = {};

        data.action = [];

        newData.cards = game_data.account.hero.cards.cards;

        newData.cards.sort(function(a, b){
            if (a.rarity < b.rarity) return -1;
            if (a.rarity > b.rarity) return 1;

            if (a.name < b.name) return -1;
            if (a.name > b.name) return 1;

            if (a.auction) return 1;

            return -1;
        });

        newData.cardsHelpCount = game_data.account.hero.cards.help_count;
        newData.cardsHelpBarrier = game_data.account.hero.cards.help_barrier;

        if (game_data.account.hero) {
            data.action = game_data.account.hero.action;
        }

        if (!pgf.base.CompareObjects(data.cards, newData.cards) ||
            data.cardsHelpCount != newData.cardsHelpCount ||
            data.cardsHelpBarrier != newData.cardsHelpBarrier) {

            data.cards = newData.cards;
            data.cardsHelpCount = newData.cardsHelpCount;
            data.cardsHelpBarrier = newData.cardsHelpBarrier;
            return true;
        }

        return false
    };

    this.Render = function() {
        RenderAction();
        RenderCards();
    };

    this.GetCurrentAction = function() {
        return data.action;
    };

    jQuery(document).bind(pgf.game.events.DATA_REFRESHED, function(e, game_data){
        if (instance.Refresh(game_data)) {
            instance.Render();
        }
        else {
            RenderAction();
        }
    });
};

pgf.game.widgets.PvPInfo = function(selector, updater, widgets, params) {
    var instance = this;

    var widget = jQuery(selector);

    var pvpInfoBlock = jQuery('.pgf-info-block-block', widget);

    var abilitiesRecords = jQuery('.pgf-pvp-ability', widget);

    var data = {};

    var processingChangeAbilitiesRequest = false;

    function RefreshAbilitiesStates() {
        abilitiesRecords.each(
            function(i, el) {
                el = jQuery(el);

                var disable = processingChangeAbilitiesRequest || data.own_hero.pvp.energy == 0;

                el.toggleClass('disabled pgf-disabled', disable);
            });
    }

    abilitiesRecords.click(
        function(e) {
            var target = jQuery(e.currentTarget);
            e.preventDefault();

            if (target.hasClass("pgf-disabled")) {
                pgf.ui.dialog.Alert({title: "Нельзя использовать способность",
                                     message: "Нельзя использовать способность: не хватает ресурсов либо изменение уже применяется."});
                return;
            }

            processingChangeAbilitiesRequest = true;

            RefreshAbilitiesStates();

            pgf.forms.Post({action: target.attr("href"),
                            data: {},
                            wait: false,
                            OnError: function() {
                                processingChangeAbilitiesRequest = false;
                                RefreshAbilitiesStates();
                            },
                            OnSuccess: function(data) {
                                processingChangeAbilitiesRequest = false;
                                RefreshAbilitiesStates();
                                jQuery(document).trigger(pgf.game.events.DATA_REFRESH_NEEDED);
                            }
                           });
        });

    function ToggleAdwantageColors(greate, good, bad, worse) {
        jQuery('.pgf-advantage-progress', widget)
            .toggleClass('progress-success', greate)
            .toggleClass('progress-info', good)
            .toggleClass('progress-warning', bad)
            .toggleClass('progress-danger', worse);
        jQuery('.pgf-advantage', widget)
            .toggleClass('label-success', greate)
            .toggleClass('label-info', good)
            .toggleClass('label-warning', bad)
            .toggleClass('label-danger', worse);
    }

    function RenderResources(element, energy, energySpeed) {
        jQuery('.pgf-pvp-energy', element).text(energy);
        jQuery('.pgf-pvp-energy-speed', element).text(energySpeed);
    }

    function RenderPvpInfo() {

        if (!data.own_hero) return;

        var ownPvP = data.own_hero.pvp;
        var enemyPvP = data.enemy_hero.pvp;

        jQuery('.pgf-advantage-percents', widget).width( ((0.5 + ownPvP.advantage * 0.5) * 100) + '%');
        jQuery('.pgf-advantage', widget).text(parseInt(ownPvP.advantage * 100) + '%');

        jQuery('.pgf-pvp-ability-ice-probability', widget).text(parseInt(ownPvP.probabilities.ice * 100) + '%');
        jQuery('.pgf-pvp-ability-blood-probability', widget).text(parseInt(ownPvP.probabilities.blood * 100) + '%');
        jQuery('.pgf-pvp-ability-flame-probability', widget).text(parseInt(ownPvP.probabilities.flame * 100) + '%');

        RenderResources(jQuery('.pgf-own-pvp-resources', widget), ownPvP.energy, ownPvP.energy_speed);

        RenderResources(jQuery('.pgf-enemy-pvp-resources', widget), enemyPvP.energy, enemyPvP.energy_speed);

        jQuery('.pgf-own-effectiveness', widget).text(Math.round(ownPvP.effectiveness));
        jQuery('.pgf-enemy-effectiveness', widget).text(Math.round(enemyPvP.effectiveness));

        if (0.5 <= ownPvP.advantage) { ToggleAdwantageColors(true, false, false, false);}
        else {
            if (0 <= ownPvP.advantage && ownPvP.advantage < 0.5) { ToggleAdwantageColors(false, true, false, false);}
            else {
                if (-0.5 <= ownPvP.advantage && ownPvP.advantage < 0) { ToggleAdwantageColors(false, false, true, false);}
                else {
                    ToggleAdwantageColors(false, false, false, true);
                }
            }
        }
    }

    this.Refresh = function(game_data) {

        if (game_data && game_data.account && game_data.account.hero) {
            data.own_hero = game_data.account.hero;
            data.enemy_hero = game_data.enemy.hero;
            RefreshAbilitiesStates();
        }
    };

    this.Render = function() {
        RenderPvpInfo();
    };

    jQuery(document).bind(pgf.game.events.DATA_REFRESHED, function(e, game_data){
        instance.Refresh(game_data);
        instance.Render();
    });
};

pgf.game.widgets.UpdateElementTooltip = function(element, tooltip, tooltipClass, tooltipsArgs) {
    if (element.data('current-tooltip') != tooltip) {
        pgf.base.HideTooltips(element, tooltipClass);
        element.data('current-tooltip', tooltip);
        if (element.data('tooltip')) {
            element.data('tooltip').options.title = tooltip;
            element.data('tooltip').enabled = true;
        }
        else {
            element.tooltip(jQuery.extend(true, {}, tooltipsArgs, {title: tooltip}));
        }
    }
};


pgf.game.widgets.Bag = function(selector, updater, widgets, params) {
    var instance = this;

    var widget = jQuery(selector);

    var bagContainer = jQuery('.pgf-bag-container', widget);
    var tabButton = jQuery('.pgf-bag-tab-button');

    var data = {};
    var oldData = {};

    function RenderItem(index, item, element) {
        element.toggleClass('rare-artifact-label', item.rarity == pgf.game.constants.ARTIFACT_RARITY.RARE.id);
        element.toggleClass('epic-artifact-label', item.rarity == pgf.game.constants.ARTIFACT_RARITY.EPIC.id);

        var tooltipClass = 'pgf-bag-artifact-tooltip';
        var tooltip = pgf.game.widgets.CreateArtifactTooltip(item, tooltipClass);
        pgf.game.widgets.UpdateElementTooltip(element, tooltip, tooltipClass, pgf.base.tooltipsArgs);

        jQuery('.pgf-name', element).text(item.name);
        jQuery('.pgf-power-container', element).toggleClass('pgf-hidden', pgf.game.constants.ARTIFACT_TYPE.USELESS.id == item.type);
        if (item.power) {
            jQuery('.pgf-physic-power', element).text(item.power[0]);
            jQuery('.pgf-magic-power', element).text(item.power[1]);
        }
        jQuery('.pgf-count-container', element).toggleClass('pgf-hidden', item.count <= 1);
        jQuery('.pgf-count', element).text(item.count);
        element.data('artifact-id', item.id);
    }

    function RenderItems() {
        var items = [];
        var counted_items = {};

        for (var uuid in data.bag) {
            var item = data.bag[uuid];
            var name = item.name + '#' + item.power;
            if (name in counted_items) {
                counted_items[name] += 1;
            }
            else {
                counted_items[name] = 1;
                items.push(item);
            }

        }

        for (var i in items) {
            var item = items[i];
            var name = item.name + '#' + item.power;
            item.count = counted_items[name];
        }

        items.sort(function(a, b){
            if (a.name > b.name) return 1;
            if (a.name < b.name) return -1;

            if (a.power > b.power) return 1;
            if (a.power < b.power) return -1;

            return 0;
        });

        pgf.base.RenderTemplateList(bagContainer, items, RenderItem, {});
    }

    this.Refresh = function(game_data) {

        var hero = widgets.heroes.CurrentHero();

        var newData = {};

        if (hero) {
            newData.bag = hero.bag;
            newData.loot_items_count = hero.secondary.loot_items_count;
            newData.max_bag_size = hero.secondary.max_bag_size;
        }
        else {
            newData = { bag: {},
                        loot_items_count: 0,
                        max_bag_size: 0};
        }

        var dataChanged = true;

        if (pgf.base.CompareObjects(oldData, newData)) {
            dataChanged = false;
        }

        oldData = jQuery.extend(true, {}, newData);
        data = newData;

        return dataChanged;
    };

    this.Render = function() {
        jQuery('.pgf-loot-items-count', tabButton).text(data.loot_items_count);
        jQuery('.pgf-max-bag-size', tabButton).text(data.max_bag_size);
        jQuery('.pgf-item-count-container', tabButton).removeClass('pgf-hidden');
        RenderItems();

        // jQuery('[rel="tooltip"]', widget).tooltip(pgf.base.tooltipsArgs);
    };

    jQuery(document).bind(pgf.game.events.DATA_REFRESHED, function(e, game_data){
        if (instance.Refresh(game_data)) {
            instance.Render();
        }
    });
};

pgf.game.widgets.CreateArtifactTooltip = function (data, cssClass) {
    var rarityName = undefined;
    var rarityClass = undefined;
    for (var i in pgf.game.constants.ARTIFACT_RARITY) {
        if (data.rarity == pgf.game.constants.ARTIFACT_RARITY[i].id) {
            rarityName = pgf.game.constants.ARTIFACT_RARITY[i].name;
            rarityClass = i.toLowerCase() + '-artifact-label';
            break;
        }
    }

    if (!rarityClass) {
        rarityClass = 'useless-artifact-label';
        rarityName = 'хлам';
    }

    var type = undefined;
    for (var i in pgf.game.constants.ARTIFACT_TYPE) {
        if (data.type == pgf.game.constants.ARTIFACT_TYPE[i].id) {
            type = pgf.game.constants.ARTIFACT_TYPE[i].name;
            break;
        }
    }

    var tooltip = '<ul class="unstyled '+cssClass+'" style="text-align: left;">';
    tooltip += '<li><h4 class="'+0+'">'+data.name+'</h4></li>';
    tooltip += '<li class="'+rarityClass+'">'+rarityName+'</li>';

    if (pgf.game.constants.ARTIFACT_TYPE.USELESS.id != data.type) tooltip += '<li>экипировка: '+type+'</li>';
    if (data.power) tooltip += '<li>физическая сила: '+data.power[0]+'</li>';
    if (data.power) tooltip += '<li>магическая сила: '+data.power[1]+'</li>';

    if (typeof data.integrity[0] == 'number' && typeof data.integrity[1] == 'number') {
        var integrityPercent = 0;
        if (data.integrity[1] > 0) {
            integrityPercent = Math.round(data.integrity[0] / data.integrity[1] * 10000) / 100;
        }
        tooltip += '<li>целостность: '+integrityPercent+'% '+'('+data.integrity[0]+' из '+data.integrity[1]+')'+'</li>';
    }
    if (data.preference_rating != null) tooltip += '<li>полезность: '+data.preference_rating+'</li>';

    if (data.effect != pgf.game.constants.NO_EFFECT_ID) tooltip += '<li><i>'+pgf.game.constants.EFFECTS[data.effect].description+'</i></li>';

    if (data.special_effect != pgf.game.constants.NO_EFFECT_ID) tooltip += '<li><i>'+pgf.game.constants.EFFECTS[data.special_effect].description+'</i></li>';

    tooltip += '</ul>';
    return tooltip;
};


pgf.game.widgets.Equipment = function(selector, updater, widgets, params) {
    var instance = this;

    var widget = jQuery(selector);

    var data = {};


    function RenderArtifact(element, data) {
        element.toggleClass('rare-artifact-label', data.rarity == pgf.game.constants.ARTIFACT_RARITY.RARE.id);
        element.toggleClass('epic-artifact-label', data.rarity == pgf.game.constants.ARTIFACT_RARITY.EPIC.id);

        var tooltipClass = 'pgf-equipment-artifact-tooltip';

        var tooltip = pgf.game.widgets.CreateArtifactTooltip(data, tooltipClass);
        pgf.game.widgets.UpdateElementTooltip(element, tooltip, tooltipClass, pgf.base.tooltipsArgs);

        jQuery('.pgf-name', element).text(data.name);
        jQuery('.pgf-physic-power', element).text(data.power[0]);
        jQuery('.pgf-magic-power', element).text(data.power[1]);
        jQuery('.pgf-power-container', element).toggleClass('pgf-hidden', false);

        element.addClass('has-artifact').data('artifact-id', data.id);
    }

    function RenderEquipment() {
        jQuery('.pgf-power-container', selector).toggleClass('pgf-hidden', true);
        for (var slot in data) {
            RenderArtifact(jQuery('.pgf-slot-'+slot, selector), data[slot]);
        }
    }

    this.Refresh = function(game_data) {

        data = game_data.account.hero.equipment;

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

    var MESSAGES_MAX_LENGTH = 100;

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

        heroData = game_data.account.hero;

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

            if (lastGameTime == turnMessages[i][1] + turnMessages[i][3]) {
                messages[0][1].push(turnMessages[i]);
            }
            else {
                messages.unshift([turnMessages[i][1], [turnMessages[i]]]);
            }

            lastGameTime = turnMessages[i][1] + turnMessages[i][3];
        }

        for (var i=0; i<=messages.length - MESSAGES_MAX_LENGTH; i++){
            messages.pop();
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

pgf.game.widgets.Abilities = function() {
    var instance = this;

    var abilities = pgf.game.constants.abilities;

    var MINIMUM_LOCK_DELAY = 750;
    var abilitiesWaitingStartTimes = {};

    var angelEnergy = 0;
    var pvpWaiting = false;
    var canParticipateInPvp = true;
    var canRepairBuilding = true;

    var canRestoreEnergy = false;

    var itemsInBag = false;

    var turn = {};

    var allowAbilityUnlock = {};

    function ChangeAbilityEnergyState(abilityType, energy) {
        jQuery('.pgf-ability-'+abilityType).toggleClass('no-energy', energy);
    }

    function ChangeAbilityWaitingState(abilityType, wait) {
        var ability = jQuery('.pgf-ability-'+abilityType);

        if (wait) {
            var date = new Date();
            abilitiesWaitingStartTimes[abilityType] = date.getTime();

            pgf.base.ToggleWait(ability, true);
        }
        else {
            var date = new Date();
            var curTime = date.getTime();
            var minCloseTime =  abilitiesWaitingStartTimes[abilityType] + MINIMUM_LOCK_DELAY;

            if ( minCloseTime <= curTime) {
                pgf.base.ToggleWait(ability, false);
            }
            else {
                window.setTimeout(function() { pgf.base.ToggleWait(ability, false); }, minCloseTime - curTime);
            }
        }
    }

    function IsProcessingAbility(abilityType) {
        return jQuery('.pgf-ability-'+abilityType).hasClass('pgf-wait');
    }

    function IsDisablingAbility(abilityType) {
        return jQuery('.pgf-ability-'+abilityType).hasClass('pgf-disable');
    }

    function ActivateAbility(element, ability) {

        var abilityInfo = abilities[ability.type];

        if (abilityInfo.cost > angelEnergy) {
            return;
        }

        if (IsProcessingAbility(ability.type)) {
            return;
        }

        if (IsDisablingAbility(ability.type)) {
            return;
        }

        ChangeAbilityWaitingState(ability.type, true);

        var buildingId = element.data('building-id');
        var battleId = element.data('battle-id');
        var redirectOnSuccess = element.data('redirect-on-success');

        pgf.forms.Post({action: pgf.urls['game:abilities:use'](ability.type, buildingId, battleId),
                        wait: false,
                        OnError: function() {
                            ChangeAbilityWaitingState(ability.type, false);
                        },
                        OnSuccess: function(data) {
                            allowAbilityUnlock[ability.type] = true;
                            ability.available_at = data.data.available_at;

                            if (buildingId != undefined) {
                                var buildingRepairDelta = jQuery('.pgf-ability-'+ability.type).data('building-repair-delta');
                                var buildingIntegrity = jQuery('.pgf-building-integrity').data('building-integrity');
                                var newIntegrity = Math.min(buildingIntegrity + buildingRepairDelta, 1.0);
                                jQuery('.pgf-building-integrity')
                                    .data('building-integrity', newIntegrity)
                                    .text(Math.round(newIntegrity*10000)/100+'%');

                                var buildingWorkers = jQuery('.pgf-building-workers').data('building-workers');
                                buildingWorkers = Math.max(0, buildingWorkers-1);
                                jQuery('.pgf-building-workers')
                                    .data('building-workers', buildingWorkers)
                                    .text(buildingWorkers);
                            }

                            if (redirectOnSuccess != undefined) {
                                setTimeout(function(){location.href = redirectOnSuccess;}, 0);
                            }
                            else {
                                jQuery(document).trigger(pgf.game.events.DATA_REFRESH_NEEDED);
                            }
                        }
                       });
    }

    function RenderAbility(ability) {

        var abilityInfo = abilities[ability.type];
        var element = jQuery('.pgf-ability-'+abilityInfo.type.toLowerCase());

        ChangeAbilityEnergyState(ability.type, abilityInfo.cost > angelEnergy);

        element.unbind('click');

        element.click(function(e){
            e.preventDefault();
            ActivateAbility(jQuery(e.currentTarget), ability);
        });
    }

    function UpdateButtons() {
        jQuery('.pgf-ability-help').toggleClass('pgf-hidden', false);

        jQuery('.pgf-ability-drop_item')
            .toggleClass('pgf-hidden', false)
            .toggleClass('no-items', !itemsInBag)
            .toggleClass('pgf-disable', !itemsInBag);

        jQuery('.pgf-ability-arena_pvp_1x1').toggleClass('pgf-hidden', pvpWaiting);
        jQuery('.pgf-in-pvp-queue-message').toggleClass('pgf-hidden', !pvpWaiting);

        jQuery('.pgf-ability-arena_pvp_1x1').toggleClass('no-registration', !canParticipateInPvp).toggleClass('pgf-disable', !canParticipateInPvp);
        jQuery('.pgf-ability-building_repair').toggleClass('no-registration', !canRepairBuilding).toggleClass('pgf-disable', !canRepairBuilding);
    }

    function RenderDeck() {
        for (var i in abilities) {
            RenderAbility(abilities[i]);
        }
        UpdateButtons();
    };

    function Refresh(game_data) {
        turn = game_data.turn;

        var hero = game_data.account.hero;

        // total energy with discount bonus
        angelEnergy = hero.energy.value + hero.energy.bonus + hero.energy.discount;

        pvpWaiting = game_data.account.in_pvp_queue;
        canParticipateInPvp = hero.permissions.can_participate_in_pvp;
        canRepairBuilding = hero.permissions.can_repair_building;

        itemsInBag = false;
        for (var uuid in hero.bag) {
            itemsInBag = true;
            break;
        }
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

    this.RenderAbility = RenderAbility;
    this.UpdateButtons = UpdateButtons;
};

pgf.game.CombineCardsDialog = function(dialog) {
    var unchosenCards = [];
    var chosenCards = [];

    var cards = widgets.actions.GetCards();

    for (var i in cards) {
        unchosenCards.push(cards[i].uid);
    }

    var button = jQuery('.pgf-do-combine-cards', dialog);

    function CanChoseCard() {
        return chosenCards.length < 3;
    }


    function GetUrl() {
        var cards = GetChoosenCards();
        return button.attr('href')+'&cards='+cards.join(',');
    }


    function GetChoosenCards() {
        var cards = [];

        jQuery('.pgf-cards-chosen .pgf-card', dialog).each(function(i, e){
            var cardUID = jQuery(e).data('card-uid');

            if (cardUID != undefined) {
                cards.push(cardUID);
            }
        });

        return cards;
    }

    function RefreshLists() {
        widgets.actions.ShowCards(jQuery('.pgf-card-choices', dialog), unchosenCards);
        widgets.actions.ShowCards(jQuery('.pgf-cards-chosen', dialog), chosenCards);

        jQuery('.pgf-card-choices .pgf-card', dialog).click(function(e){
            e.preventDefault();

            if (!CanChoseCard()) {
                return;
            }

            var el = jQuery(e.currentTarget);
            ChoseCard(el.data('card-uid'));
        });

        jQuery('.pgf-cards-chosen .pgf-card', dialog).click(function(e){
            e.preventDefault();
            var el = jQuery(e.currentTarget);
            UnchoseCard(el.data('card-uid'));
        });
    }

    RefreshLists();

    function ChoseCard(cardUID) {
        unchosenCards.splice(unchosenCards.indexOf(cardUID), 1);
        chosenCards.push(cardUID);
        RefreshLists();
    }

    function UnchoseCard(cardUID) {
        chosenCards.splice(chosenCards.indexOf(cardUID), 1);
        unchosenCards.push(cardUID);
        RefreshLists();
    }

    button.click(function(e){
        e.preventDefault();

        pgf.forms.Post({ action: GetUrl(),
                         OnSuccess: function(data){
                             jQuery(document).trigger(pgf.game.events.DATA_REFRESH_NEEDED);
                             dialog.modal('hide');

                             pgf.ui.dialog.Alert({message: data.data.message,
                                                  title: 'Карты объединены'});
                         }
                       });


    });

};
