
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
pgf.game.events.DIARY_REFRESHED = 'pgf-diary-refreshed';


pgf.game.GetRaceText = function(race, gender) {
    if (gender == 1) return pgf.game.constants.RACE_TO_TEXT[race].female;
    return pgf.game.constants.RACE_TO_TEXT[race].male;
};

pgf.game.GetPersonalityPracticalText = function(personality, gender) {
    if (gender == 1) return pgf.game.constants.PERSONALITY_PRACTICAL_TO_TEXT[personality].female;
    return pgf.game.constants.PERSONALITY_PRACTICAL_TO_TEXT[personality].male;
};

pgf.game.GetPersonalityCosmeticText = function(personality, gender) {
    if (gender == 1) return pgf.game.constants.PERSONALITY_COSMETIC_TO_TEXT[personality].female;
    return pgf.game.constants.PERSONALITY_COSMETIC_TO_TEXT[personality].male;
};


pgf.game.Updater = function(params) {

    var INITIAL_REFRESH_DELAY = 1000;

    var instance = this;
    var refreshInterval = undefined;
    var refreshTimer = undefined;
    var refreshDelay = INITIAL_REFRESH_DELAY;

    var autoRefreshStopped = false;

    var oldDatas = {}; // turn_number: data
    var currentTurn = undefined;

    var lastDiaryVersion = undefined;
    var diaryRefreshGoing = false;


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

        if (currentTurn > newData.turn.number) {
            return true;
        }

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

    instance.RefreshDiary = function() {
        if (!params.diaryUrl) {
            return;
        }

        if (instance.diaryRefreshGoing) {
            return;
        }

        instance.diaryRefreshGoing = true;

        jQuery.ajax({
            dataType: 'json',
            type: 'get',
            url: params.diaryUrl,

            success: function(data, request, status) {
                instance.lastDiaryVersion = data.data.version;
                jQuery(document).trigger(pgf.game.events.DIARY_REFRESHED, data.data);
            },
            error: function() {
            },
            complete: function() {
                instance.diaryRefreshGoing = false;
            }
        });
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
                        refreshDelay = Math.min(refreshDelay * 1.618, 16.18*1000); //the golden ratio
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

                if (instance.data.account && instance.data.account.hero.diary != instance.lastDiaryVersion) {
                    instance.RefreshDiary();
                }

                setTimeout(function(e){
                    jQuery('.pgf-wait-data').toggleClass('pgf-hidden', true);

                    if (jQuery('.pgf-game-data').hasClass('pgf-hidden')) {
                        jQuery('.pgf-game-data').toggleClass('pgf-hidden', false);

                        if (pgf.game.map) {
                            jQuery(document).trigger(pgf.game.map.events.MAP_RESIZED);
                        }
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
    var account = undefined;

    var tooltipArgs = jQuery.extend(true, {}, pgf.base.tooltipsArgs, {title: function(){return jQuery('.pgf-might-tooltip', content).html();},
                                                                      placement: "bottom"});
    jQuery('.pgf-might-record', content).tooltip(tooltipArgs);

    this.RenderHero = function(data, widget) {

        if (!data) return;

        var heroPageUrl = '/game/heroes/'+data.id;

        jQuery('.pgf-level', widget).text(data.base.level);
        jQuery('.pgf-destiny-points', widget).text(data.base.destiny_points);
        jQuery('.pgf-name', widget).text(data.base.name);
        jQuery('.pgf-hero-page-link', widget).attr('href', heroPageUrl);
        jQuery('.pgf-free-destiny-points', widget).attr('href', heroPageUrl+'#hero-tab-main=attributes').toggleClass('pgf-hidden', !data.base.destiny_points);

        jQuery('.pgf-health', widget).text(parseInt(data.base.health));
        jQuery('.pgf-max-health', widget).text(data.base.max_health);

        jQuery('.pgf-diary-block-health').text(parseInt(data.base.health));
        jQuery('.pgf-diary-block-max-health').text(data.base.max_health);

        jQuery('.pgf-experience', widget).text(parseInt(data.base.experience));
        jQuery('.pgf-experience-to-level', widget).text(data.base.experience_to_level);

        jQuery('.pgf-diary-block-experience').text(parseInt(data.base.experience));
        jQuery('.pgf-diary-block-experience-to-level').text(data.base.experience_to_level);

        jQuery('.pgf-race-gender').removeClass('pgf-hidden');
        jQuery('.pgf-race', widget).text(pgf.game.GetRaceText(data.base.race, data.base.gender));

        jQuery('.pgf-health-percents', widget).width( (100 * data.base.health / data.base.max_health) + '%');
        jQuery('.pgf-experience-percents', widget).width( (100 * data.base.experience / data.base.experience_to_level) + '%');

        jQuery('.pgf-physic-power', widget).text(data.secondary.power[0]);
        jQuery('.pgf-magic-power', widget).text(data.secondary.power[1]);
        jQuery('.pgf-money', widget).text(parseInt(data.base.money));
        jQuery('.pgf-might', widget).text(Math.round(data.might.value*100)/100);
        jQuery('.pgf-might-crit-chance', widget).text(Math.round(data.might.crit_chance*10000)/100.0);
        jQuery('.pgf-might-pvp-effectiveness-bonus', widget).text(Math.round(data.might.pvp_effectiveness_bonus*10000)/100.0);
        jQuery('.pgf-might-politics-power-bonus', widget).text(Math.round(data.might.politics_power*10000)/100.0);

        jQuery('.pgf-energy', content).text(account.energy);
        jQuery('.pgf-diary-block-energy').text(account.energy);

        // companion data
        jQuery('.pgf-companion', widget).toggleClass('pgf-hidden', !!(data.companion == null));
        jQuery('.pgf-no-companion', widget).toggleClass('pgf-hidden', !(data.companion == null));

        if (data.companion) {
            jQuery('.pgf-companion-info-link', widget).data('companion-id', data.companion.type);
            jQuery('.pgf-companion-info-link.pgf-alive', widget).toggleClass('pgf-hidden', data.companion.health === 0);
            jQuery('.pgf-companion-info-link.pgf-dead', widget).toggleClass('pgf-hidden', data.companion.health !== 0);

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
        account = game_data.account;
        data = game_data.account.hero;

        if (params.dataMode == 'pvp_enemy') {
            account = game_data.enemy;
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

    var gameDate = jQuery('.pgf-game-date');
    var gameTime = jQuery('.pgf-game-time');

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

        if (data.clan_id == undefined) {
            nameElement.text(data.name);

            popoverTitle = 'Мастер';

            var place = widgets.mapManager.GetPlaceData(data.place);
            var race = pgf.game.GetRaceText(data.race, data.gender);
            var personalityPractical = pgf.game.GetPersonalityPracticalText(data.personality.practical, data.gender)
            var personalityCosmetic = pgf.game.GetPersonalityCosmeticText(data.personality.cosmetic, data.gender)
            var profession = pgf.game.constants.PERSON_TYPE_TO_TEXT[data.profession];

            var content = jQuery('#pgf-popover-person').clone();

            if (place) {
                jQuery('.pgf-place', content).text(place.name);
            }

            jQuery('.pgf-race', content).text(race);
            jQuery('.pgf-personality-practical', content).text(personalityPractical);
            jQuery('.pgf-personality-cosmetic', content).text(personalityCosmetic);
            jQuery('.pgf-type', content).text(profession);

            nameElement.click(function(e){
                e.preventDefault();
                widgets.map.CenterOnPlace(place.id);
            });
        }
        else {
            nameElement.text(data.name);

            popoverTitle = 'Эмиссар';

            var place = widgets.mapManager.GetPlaceData(data.place);
            var race = pgf.game.GetRaceText(data.race, data.gender);

            var content = jQuery('#pgf-popover-emissary').clone();

            if (place) {
                jQuery('.pgf-place', content).text(place.name);
            }

            jQuery('.pgf-race', content).text(race);

            nameElement.click(function(e){
                e.preventDefault();
                widgets.map.CenterOnPlace(place.id);
            });
        }
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


pgf.game.widgets.Action = function(selector, updater, widgets, params) {
    var instance = this;

    var widget = jQuery(selector);

    var actionBlock = jQuery('.pgf-current-action-block', widget);
    var actionInfo = jQuery('.pgf-action-info', widget);

    var cardsListContainer = jQuery('.pgf-cards-container', widget)
    var arenaBattlesListContainer = jQuery('.pgf-arena-battles-container', widget)

    var cardsDropdownCountrol = jQuery('.pgf-cards-for-use-dropdown', widget);
    var arenaDropdownCountrol = jQuery('.pgf-arena-dropdown', widget);

    var data = {};

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

    function RenderCardProgress() {
    }

    function RenderCards() {
        // jQuery('.pgf-cards-choices .pgf-card', widget).toggleClass('pgf-hidden', true);

        if (widgets.cards) {
            jQuery('.pgf-cards-choices .pgf-no-cards', widget).toggleClass('pgf-hidden', widgets.cards.HasCardsInHand());
            widgets.cards.RenderHand(cardsListContainer);
        }

        jQuery('.pgf-card-link', cardsListContainer).off().click(function(e) {
            e.preventDefault();
            if (widgets.cards) {
                widgets.cards.Use(jQuery('.pgf-card-record', e.currentTarget).data('ids')[0]);
            }
        });

        jQuery('.pgf-get-card-button', widget).off().click(function(e){
            e.preventDefault();
            e.stopPropagation();
            if (widgets.cards) {
                widgets.cards.GetCard();
            }
            cardsDropdownCountrol.dropdown('toggle');
        });

        jQuery('.pgf-storage-card-button', widget).off().click(function(e){
            e.preventDefault();
            e.stopPropagation();
            if (widgets.cards) {
                widgets.cards.OpenStorageDialog();
            }
            cardsDropdownCountrol.dropdown('toggle');
        });

        jQuery('.pgf-transformator-card-button').off().click(function(e){
            e.preventDefault();
            e.stopPropagation();
            if (widgets.cards) {
                widgets.cards.OpenTransformatorDialog();
            }
            cardsDropdownCountrol.dropdown('toggle');
        });
    }

    function RenderArena() {
        // jQuery('.pgf-arena-choices .pgf-card', widget).toggleClass('pgf-hidden', true);

        if (widgets.pvp) {
            jQuery('.pgf-arena-choices .pgf-no-arena-battle-requests', widget).toggleClass('pgf-hidden', widgets.pvp.HasBattleRequests());
            jQuery('.pgf-arena-battles-table', widget).toggleClass('pgf-hidden', !widgets.pvp.HasBattleRequests());

            jQuery('.pgf-arena-battle-requests-amount', widget).text(widgets.pvp.BattlesAmount());

            jQuery('.pgf-arena-pvp-with-players', widget).text(widgets.pvp.BattlesWithPlayers());
            jQuery('.pgf-arena-pvp-with-bots', widget).text(widgets.pvp.BattlesWithBots());

            var hasRequestFromAccount = false;

            var hero = widgets.heroes.CurrentHero();

            if (hero) {
                hasRequestFromAccount = widgets.pvp.HasRequestFromAccount(hero.id);
            }

            jQuery('.pgf-arena-call-active').toggleClass('pgf-hidden', !hasRequestFromAccount);

            jQuery('.pgf-call-to-battle', widget).toggleClass('pgf-hidden', hasRequestFromAccount);
            jQuery('.pgf-leave-arena', widget).toggleClass('pgf-hidden', !hasRequestFromAccount);

            widgets.pvp.RenderArenaBattleRequests(arenaBattlesListContainer);
        }

        jQuery('.pgf-call-to-battle', widget).off().click(function(e) {
            e.preventDefault();
            e.stopPropagation();

            if (widgets.pvp) {
                widgets.pvp.CallToArena();
            }
        });

        jQuery('.pgf-arena-bot-fight', widget).off().click(function(e) {
            e.preventDefault();
            e.stopPropagation();

            if (widgets.pvp) {
                widgets.pvp.CreateArenaBotBattle();
            }
        });

        jQuery('.pgf-leave-arena', widget).off().click(function(e) {
            e.preventDefault();
            e.stopPropagation();

            if (widgets.pvp) {
                widgets.pvp.LeaveArena();
            }
        });

    }

    this.Refresh = function(game_data) {

        var newData = {};

        data.action = [];

        if (game_data.account.hero) {
            data.action = game_data.account.hero.action;
        }

        return false
    };

    this.Render = function() {
        RenderAction();
        RenderCards();
        RenderArena();
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
            RenderArena();
        }
    });

    jQuery(document).bind(pgf.game.events.CARDS_REFRESHED, function(e){
        if (widgets.cards) {
            RenderCards();
        }
    });

    jQuery(document).bind(pgf.game.events.PVP_REFRESHED, function(e){
        if (widgets.pvp) {
            RenderArena();
        }
    });

    jQuery(".pgf-cards-for-use-dropdown", widget).click(function(e){
        e.preventDefault();
        if (widgets.cards) {
            widgets.cards.GetCards();
        }
    });

    jQuery(".pgf-arena-dropdown", widget).click(function(e){
        e.preventDefault();
        if (widgets.pvp) {
            widgets.pvp.GetInfo();
        }
    });

    jQuery('.pgf-action-info-link').click(function(e){
        e.preventDefault();
        var target = jQuery(e.currentTarget);
        var url = target.attr('href');
        pgf.ui.dialog.Create({ fromUrl: url});
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

                var disable = processingChangeAbilitiesRequest || data.own_hero.action.data.pvp.energy == 0;

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

        var ownPvP = data.own_hero.action.data.pvp;
        var enemyPvP = data.enemy_hero.action.data.pvp;

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
        pgf.base.UpdateElementTooltip(element, tooltip, tooltipClass, pgf.base.tooltipsArgs);

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
        pgf.base.UpdateElementTooltip(element, tooltip, tooltipClass, pgf.base.tooltipsArgs);

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

    var SHOW_ARTISTIC_TEXT = (pgf.base.settings.get("log_artistic_text", 'true') == 'true');
    var SHOW_TECHNICAL_TEXT = (pgf.base.settings.get("log_technical_text", 'true') == 'true');

    function SetTextMode(artistic, technical) {
        SHOW_ARTISTIC_TEXT = artistic;
        SHOW_TECHNICAL_TEXT = technical;

        pgf.base.settings.set("log_artistic_text", SHOW_ARTISTIC_TEXT);
        pgf.base.settings.set("log_technical_text", SHOW_TECHNICAL_TEXT);

        UpdateModeButtonsVisibility();
        instance.Render();
    }

    function UpdateModeButtonsVisibility() {
        jQuery('.pgf-log-mode').toggleClass('pgf-hidden', true);
        jQuery('.pgf-log-mode-technical').toggleClass('pgf-hidden', !(!SHOW_ARTISTIC_TEXT && SHOW_TECHNICAL_TEXT));
        jQuery('.pgf-log-mode-artistic').toggleClass('pgf-hidden', !(SHOW_ARTISTIC_TEXT && !SHOW_TECHNICAL_TEXT));
        jQuery('.pgf-log-mode-all').toggleClass('pgf-hidden', !(SHOW_ARTISTIC_TEXT && SHOW_TECHNICAL_TEXT));
    };

    UpdateModeButtonsVisibility();

    jQuery('.pgf-log-mode').click(function(e) {
        if (SHOW_ARTISTIC_TEXT && SHOW_TECHNICAL_TEXT) {
            SetTextMode(true, false);
            return;
        }
        if (SHOW_ARTISTIC_TEXT && !SHOW_TECHNICAL_TEXT) {
            SetTextMode(false, true);
            return;
        }
        if (!SHOW_ARTISTIC_TEXT && SHOW_TECHNICAL_TEXT) {
            SetTextMode(true, true);
            return;
        }
    });

    function ShortInfoJournal(message) {
        var shortInfo = "";
        var key = message[3]

        if (key in pgf.game.constants.linguistics_formatters) {
            shortInfo = ' ' + pgf.game.constants.linguistics_formatters[key];
            var variables = message[4];
            for (variable in variables) {
                shortInfo = shortInfo.replace('!'+variable+'!', variables[variable].charAt(0).toUpperCase() + variables[variable].slice(1));
            }
        }
        return shortInfo;
    }

    function ShortInfoDiary(message) {
        var shortInfo = "";
        var key = message.type

        if (key in pgf.game.constants.linguistics_formatters) {
            shortInfo = ' ' + pgf.game.constants.linguistics_formatters[key];
            var variables = message.variables;
            for (variable in variables) {
                shortInfo = shortInfo.replace('!'+variable+'!', variables[variable].charAt(0).toUpperCase() + variables[variable].slice(1));
            }
        }
        return shortInfo;
    }

    function RenderDiaryMessage(index, message, element) {

        var text = "";
        for (var i in message[1]) {
            var shortInfo = ShortInfoDiary(message[1][i]);
            var intenalText = (SHOW_ARTISTIC_TEXT || !shortInfo ? message[1][i].message : "") + (SHOW_TECHNICAL_TEXT ? shortInfo : "");
            if (i == 0) {
                text += "<div class='submessage' style='vertical-align: top;'>" + intenalText + "</div>";
            }
            else {
                text += "<div class='submessage'>" + intenalText + "</div>";
            }
        }

        jQuery('.pgf-time', element).text(message[1][0].game_date);
        jQuery('.pgf-date', element).text(message[0]);
        jQuery('.pgf-position', element).text(message[1][0].position.charAt(0).toUpperCase() + message[1][0].position.slice(1));
        jQuery('.pgf-message', element).html(text);
    }

    function RenderLogMessage(index, message, element) {
        jQuery('.pgf-time', element).text(message[0]);

        var text = "";
        for (var i in message[1]) {
            var shortInfo = ShortInfoJournal(message[1][i]);
            var intenalText = (SHOW_ARTISTIC_TEXT || !shortInfo ? message[1][i][2] : "") + (SHOW_TECHNICAL_TEXT ? shortInfo : "");
            if (i == 0) {
                text += "<div class='submessage' style='vertical-align: top;'>" + intenalText + "</div>";
            }
            else {
                text += "<br/><div class='submessage'>" + intenalText + "</div>";
            }
        }

        jQuery('.pgf-message', element).html(text);
    }

    function RenderLog(data, widget) {

        var messagesToRender = messages;

        if (messagesToRender.length == 0 && params.type == 'log') {
            messagesToRender = [['', [[0, '21:50', 'Ищем героя…', -1, {}]]]];
        }

        if (params.type == 'log') {
            pgf.base.RenderTemplateList(shortLogContainer, messagesToRender, RenderLogMessage, {});
        }
        if (params.type == 'diary') {
            pgf.base.RenderTemplateList(shortLogContainer, messagesToRender, RenderDiaryMessage, {});
        }

    }

    this.RefreshJournal = function(turnMessages) {
        var lastTimestamp = -1;
        var lastGameTime = undefined;

        if (messages.length > 0)  messages.shift(); // if messages has elements, remove last since it can be not full

        if (messages.length > 0) lastTimestamp = messages[0][1][messages[0][1].length-1][0]; //get linux timestamp
        if (messages.length > 0) lastGameTime = messages[0][0]; //get game time

        for (var i=0; i<=turnMessages.length-1; ++i) {

            if (turnMessages[i][0] <= lastTimestamp) continue;

            if (lastGameTime == turnMessages[i][1] + turnMessages[i][5]) {
                messages[0][1].push(turnMessages[i]);
            }
            else {
                messages.unshift([turnMessages[i][1], [turnMessages[i]]]);
            }

            lastGameTime = turnMessages[i][1] + turnMessages[i][5];
        }

        for (var i=0; i<=messages.length - MESSAGES_MAX_LENGTH; i++){
            messages.pop();
        }

    };

    this.RefreshDiary = function(turnMessages) {
        var lastTimestamp = -1;
        var lastGameTime = undefined;

        if (messages.length > 0) {
            messages.shift(); // if messages has elements, remove last since it can be not full
        }

        if (messages.length > 0) {
            var lastMessage = messages[0][1][messages[0][1].length-1];

            lastTimestamp = lastMessage.timestamp;
            lastGameTime = lastMessage.game_time;
        }

        for (var i=0; i<=turnMessages.length-1; ++i) {

            var message = turnMessages[i];

            if (message.timestamp <= lastTimestamp) continue;

            if (lastGameTime == message.game_time + message.game_date) {
                messages[0][1].push(message);
            }
            else {
                messages.unshift([message.game_time, [message]]);
            }

            lastGameTime = message.game_time + message.game_date;
        }

        for (var i=0; i<=messages.length - MESSAGES_MAX_LENGTH; i++){
            messages.pop();
        }

    };

    this.Render = function() {
        RenderLog();
    };

    jQuery(document).bind(pgf.game.events.DATA_REFRESHED, function(e, game_data){
        if (params.type == 'log') {
            instance.RefreshJournal(game_data.account.hero.messages);
            instance.Render();
        }
    });

    jQuery(document).bind(pgf.game.events.DIARY_REFRESHED, function(e, diary){
        if (params.type == 'diary') {
            instance.RefreshDiary(diary.messages);
            instance.Render();
        }
    });
};

pgf.game.widgets.Abilities = function() {
    var instance = this;

    var abilities = pgf.game.constants.abilities;

    var MINIMUM_LOCK_DELAY = 750;
    var abilitiesWaitingStartTimes = {};

    var angelEnergy = 0;

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

        var battleId = element.data('battle-id');
        var redirectOnSuccess = element.data('redirect-on-success');

        var url = '/game/abilities/'+ability.type+'/api/use?api_version=1.0&api_client='+API_CLIENT;

        if (battleId != undefined) {
            url = url + '&battle=' + battleId;
        }

        pgf.forms.Post({action: url,
                        wait: false,
                        OnError: function() {
                            ChangeAbilityWaitingState(ability.type, false);
                        },
                        OnSuccess: function(data) {
                            allowAbilityUnlock[ability.type] = true;
                            ability.available_at = data.data.available_at;

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
    }

    function RenderDeck() {
        for (var i in abilities) {
            RenderAbility(abilities[i]);
        }
        UpdateButtons();
    };

    function Refresh(game_data) {
        turn = game_data.turn;

        var account = game_data.account;
        var hero = game_data.account.hero;

        angelEnergy = account.energy;

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
