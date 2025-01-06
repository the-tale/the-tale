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

pgf.game.events.CARDS_REFRESHED = 'pgf-cards-refreshed';
pgf.game.events.CARDS_TIMER_DATA = 'pgf-cards-timer-data';


pgf.game.widgets.CreateCardTooltip = function (data, cssClass) {
    var rarityClass = pgf.game.constants.CARD_RARITY[data.rarity].name.toLowerCase()+'-card-label';
    var rarityName = pgf.game.constants.CARD_RARITY[data.rarity].text;
    var description = pgf.game.constants.CARD_TYPE[data.type].description;
    var combiners = pgf.game.constants.CARD_TYPE[data.type].combiners;

    var tooltip = '<ul class="unstyled '+cssClass+'" style="text-align: left;">';
    tooltip += '<li><h4>'+data.name+'</h4></li>';
    tooltip += '<li class="'+rarityClass+'">'+rarityName+'</li>';
    tooltip += '<li>'+description+'</li>';
    tooltip += '<hr/>';

    if (data.inDeckToTrade) {
        tooltip += '<li><i>карт для продажи на рынке: ' + data.inDeckToTrade + '</i></li>';
    }
    else {
        tooltip += '<li><i>нет карт для продажи на рынке</i></li>';
    }

    for (var i in combiners) {
        tooltip += '<li><strong>' + combiners[i] + '</strong></li>'
    }

    tooltip += '</ul>';
    return tooltip;
};


pgf.game.widgets.GetCardsTooltipArgs = function() {
    var cardTooltipArgs = jQuery.extend({}, pgf.base.tooltipsArgs);

    cardTooltipArgs.placement = function(tip, element) {
        var offset = jQuery(element).offset();
        if (offset.left == 0 && offset.top == 0) {
            jQuery(tip).addClass('pgf-hidden');
        }
        // по-умолчанию показываем слева, так как названия карт всегда выравнены по левому краю
        // поэтому тултип слева всегда будет около названия, а справа может появиться далеко в случае широкого поля или короткого названия карты
        if (offset.left < pgf.base.TOOLTIP_WIDTH) {
            return 'right'
        }
        else {
            return 'left'
        }
    }

    return cardTooltipArgs;
};


pgf.game.widgets.RenderCard = function(index, item, element) {
    jQuery('.pgf-number', element).text(item.total);
    jQuery('.pgf-card-record', element)
        .text(item.name.charAt(0).toUpperCase() + item.name.slice(1))
        .addClass(pgf.game.constants.CARD_RARITY[item.rarity].name.toLowerCase()+'-card-label')
        .data('ids', item.ids);

    var tooltipClass = 'pgf-card-tooltip';
    var tooltip = pgf.game.widgets.CreateCardTooltip(item, tooltipClass);
    pgf.base.UpdateElementTooltip(element, tooltip, tooltipClass, pgf.game.widgets.GetCardsTooltipArgs());
};


pgf.game.widgets.CardsComparator = function(a, b) {
    if (a.rarity < b.rarity) return -1;
    if (a.rarity > b.rarity) return 1;
    if (a.name < b.name) return -1;
    if (a.name > b.name) return 1;
    return 0;
};


pgf.game.widgets.PrepairCardsRenderSequence = function(cardInfos) {
    var cardsByType = {};

    for (var i in cardInfos) {
        var cardInfo = cardInfos[i];

        if (!(cardInfo.name in cardsByType)) {
            cardsByType[cardInfo.name] = {total: 0,
                                          inDeckToTrade: 0,
                                          type: cardInfo.type,
                                          rarity: cardInfo.rarity,
                                          ids: [],
                                          name: cardInfo.name};
        }

        cardsByType[cardInfo.name].total += 1;

        if (cardInfo.auction) {
            cardsByType[cardInfo.name].inDeckToTrade += 1;
            cardsByType[cardInfo.name].ids.push(cardInfo.uid); // tradable cards at the tail of list
        }
        else {
            cardsByType[cardInfo.name].ids.unshift(cardInfo.uid); // nontradable cards at the head of list
        }
    }

    var cards = [];

    for (var i in cardsByType) {
        cards.push(cardsByType[i]);
    }

    cards.sort(pgf.game.widgets.CardsComparator);

    return cards
};


pgf.game.widgets.CardsProgress = function (params) {
    var instance = this;

    instance.data = null;
    instance.requestCounter = 0;

    function Refresh() {
        /* code is disabled due moving the game to the readonly mode */
        return;

        if (instance.data == null) {
            return
        }

        var now = (new Date()).getTime() / 1000;

        var timer = instance.data.newCardTimer;

        var resources = Math.min(timer.resources + timer.speed * (now - timer.resources_at), timer.border);

        var finishAfter = timer.finish_at - now;

        if (finishAfter < 0) {
            var counter = Math.log(-finishAfter);

            if (instance.requestCounter < counter) {
                instance.requestCounter = counter + 1;
                params.cards.GetCards();
            }

            finishAfter = 0;
        }
        else {
            instance.requestCounter = 0;
        }

        jQuery('.pgf-new-card-progress', params.container).width((resources / timer.border)*100+'%');
        jQuery('.pgf-new-cards-timer', params.container).text(pgf.base.FormatTimeDelta(finishAfter));

        jQuery('.pgf-get-card-button', params.container).toggleClass('pgf-hidden', instance.data.newCardsNumber == 0);
        jQuery('.pgf-new-cards-number', params.container).text(instance.data.newCardsNumber);

        jQuery('.pgf-new-card-icon').toggleClass('pgf-hidden', instance.data.newCardsNumber == 0);

    }

    // instance.Update = function(newCardsNumber, timer) {
    //     jQuery('.pgf-cards-choices .pgf-card', widget).toggleClass('pgf-hidden', true);
    // }

    jQuery(document).bind(pgf.game.events.CARDS_TIMER_DATA, function(e, timerData){
        instance.data = timerData;
    });

    var refreshTimer = setInterval(Refresh, 1000);
}


pgf.game.widgets.Cards = function (params) {

    var instance = this;

    instance.data = {cards: {},
                     hand: [],
                     storage: [],
                     transformator: [],
                     cardsInTransformator: []};

    var localVersion = 0;
    var firstRequest = true;

    function Refresh() {
        instance.data.hand = [];
        instance.data.storage = [];
        instance.data.transformator = [];

        for (var i in instance.data.cards) {
            var card = instance.data.cards[i];

            if (jQuery.inArray(card.uid, instance.data.cardsInTransformator) != -1) {
                instance.data.transformator.push(card)
                continue;
            }

            if (card.in_storage) {
                instance.data.storage.push(card);
            }
            else {
                instance.data.hand.push(card);
            }
        }
    }

    this.GetCards = function() {
        /* code is disabled due moving the game to the readonly mode */
        return;

        var requestedVersion = localVersion + 1;

        jQuery.ajax({
            dataType: 'json',
            type: 'get',
            url: params.getItems,

            success: function(data, request, status) {

                if (requestedVersion <= localVersion) {
                    instance.GetCards();
                    return;
                }

                localVersion = requestedVersion;

                var oldKeys = [];
                var newKeys = [];

                for (var uid in instance.data.cards)  {
                    oldKeys.push(uid);
                }

                for (var i in data.data.cards) {
                    var card = data.data.cards[i];
                    newKeys.push(card.uid);
                }

                oldKeys.sort();
                newKeys.sort();

                var cardsChanged = !(JSON.stringify(oldKeys) == JSON.stringify(newKeys));

                instance.data.cards = {}

                for (var i in data.data.cards) {
                    var card = data.data.cards[i];
                    instance.data.cards[card.uid] = card;
                }

                jQuery(document).trigger(pgf.game.events.CARDS_TIMER_DATA, {newCardsNumber: data.data.new_cards,
                                                                            newCardTimer: data.data.new_card_timer});

                if (cardsChanged || firstRequest) {
                    Refresh();
                    jQuery(document).trigger(pgf.game.events.CARDS_REFRESHED);
                }

                firstRequest = false;
            },
            error: function() {
            },
            complete: function() {
            }
        });
    };

    this.GetCard = function() {
        pgf.forms.Post({ action: params.getCard,
                         OnSuccess: function(data){
                             instance.GetCards();
                             instance.OpenNewCardsDialog(data.data.cards);
                         }
                       });
    };

    this.RenderHand = function(widget) {
        var cards = pgf.game.widgets.PrepairCardsRenderSequence(instance.data.hand);
        pgf.base.RenderTemplateList(widget, cards, pgf.game.widgets.RenderCard, {});
    };

    this.RenderStorage = function(widget) {
        var cards = pgf.game.widgets.PrepairCardsRenderSequence(instance.data.storage);
        pgf.base.RenderTemplateList(widget, cards, pgf.game.widgets.RenderCard, {});
    };

    this.RenderTransformator = function(widget) {
        var cards = pgf.game.widgets.PrepairCardsRenderSequence(instance.data.transformator);
        pgf.base.RenderTemplateList(widget, cards, pgf.game.widgets.RenderCard, {});
    };

    this.HasCardsInHand = function() {return instance.data.hand.length > 0;};

    this.CanTransform = function() {
        if (instance.data.transformator.length == 0) return false;

        ////////////////////////////////////////////////////////////
        // плохое решение, но полноценно прокидывать правила преобразования в интерфейс сложно

        // проверяем, объединение 9 x EMISSARY_QUEST -> CREATE_CLAN
        if (instance.data.transformator.length == 9) {
            var all_emissary_quests = true;

            for(var i in instance.data.transformator) {
                var card = instance.data.transformator[i];

                all_emissary_quests = all_emissary_quests && (card.type === 157);
            }
            if (all_emissary_quests) {
                return true;
            }
        }

        ////////////////////////////////////////////////////////////

        if (instance.data.transformator.length > 3) return false;

        var rarity = instance.data.transformator[0].rarity;

        if (instance.data.transformator.length == 1 && rarity == 0) return false;

        for (var i in instance.data.transformator) {
            var card = instance.data.transformator[i];
            if (rarity != card.rarity) return false;
        }

        if (instance.data.transformator.length == 3 && rarity == 4) return false;

        return true;
    }

    this.OpenNewCardsDialog = function(newCards) {
        pgf.ui.dialog.Create({ fromString: pgf.game.widgets.NEW_CARDS_DIALOG,
                               OnOpen: function(dialog) {
                                   pgf.game.NewCardsDialog(dialog, newCards);
                               }
                             });
    };

    this.OpenStorageDialog = function() {
        pgf.ui.dialog.Create({ fromString: pgf.game.widgets.CARDS_STORAGE_DIALOG,
                               OnOpen: function(dialog) {
                                   pgf.game.CardsStorageDialog(dialog, instance);
                               }
                             });
    };

    this.OpenTransformatorDialog = function() {
        pgf.ui.dialog.Create({ fromString: pgf.game.widgets.CARDS_TRANSFORMATOR_DIALOG,
                               OnOpen: function(dialog) {
                                   pgf.game.CardsTransformatorDialog(dialog, instance);
                               },
                               OnClosed: function(dialog) {
                                   instance.RemoveAllCardsFromTransformator();
                               }
                             });
    };

    var ChangeStorage = function(cardsIds, inStorage, url, errorMessage) {
        localVersion += 1;

        data = new FormData();

        for (var i in cardsIds) {
            var card = instance.data.cards[cardsIds[i]];
            card.in_storage = inStorage;
            data.append('card', card.uid);
        }

        function Undo(message) {
            localVersion += 1;

            for (var i in cardsIds) {
                instance.data.cards[cardsIds[i]].in_storage = false;
            }

            pgf.ui.dialog.Error({message: message});

            Refresh();

            jQuery(document).trigger(pgf.game.events.CARDS_REFRESHED);
        }

        jQuery.ajax({
            dataType: 'json',
            type: 'post',
            url: url,
            data: data,
            contentType: false,
            processData: false,
            success: function(data, request, status) {
                if (data.status == 'error') {
                    Undo(data.error);
                    return;
                }

                localVersion += 1;
            },
            error: function() {
                Undo(errorMessage);
            }
        });

        Refresh();

        jQuery(document).trigger(pgf.game.events.CARDS_REFRESHED);
    };

    this.ToStorage = function(cardsIds) {
        ChangeStorage(cardsIds,
                      true,
                      params.moveToStorage,
                      'Неизвестная ошибка при перемещении карт в хранилище. Пожалуйста, обновите страницу.');
    };

    this.ToHand = function(cardsIds) {
        ChangeStorage(cardsIds,
                      false,
                      params.moveToHand,
                      'Неизвестная ошибка при перемещении карт в руку. Пожалуйста, обновите страницу.');
    };

    this.ToTransformator = function(cardId) {
        if (jQuery.inArray(cardId, instance.data.cardsInTransformator) != -1) {
            return;
        }

        instance.data.cardsInTransformator.push(cardId);

        Refresh();
    };

    this.FromTransformator = function(cardId) {
        if (jQuery.inArray(cardId, instance.data.cardsInTransformator) == -1) {
            return;
        }

        instance.data.cardsInTransformator.splice(instance.data.cardsInTransformator.indexOf(cardId), 1);

        Refresh();
    };

    this.RemoveAllCardsFromTransformator = function() {
        for (var i in instance.data.cardsInTransformator.slice()) {
            cardId = instance.data.cardsInTransformator[i];
            instance.data.cardsInTransformator.splice(instance.data.cardsInTransformator.indexOf(cardId), 1);
        }

        Refresh();
    }

    this.Transform = function() {
        if (!instance.CanTransform()) return;

        localVersion += 1;

        data = new FormData();

        var ids = [];

        for (var i in instance.data.transformator) {
            var card = instance.data.transformator[i];
            ids.push(card.uid);
            data.append('card', card.uid);
        }

        pgf.ui.dialog.wait('start');

        jQuery.ajax({
            dataType: 'json',
            type: 'post',
            url: params.transformItems,
            data: data,
            contentType: false,
            processData: false,

            success: function(data, request, status) {
                if (data.status == 'error') {
                    pgf.ui.dialog.wait('stop', stopCallback=function(){
                        pgf.ui.dialog.Error({message: data.error});
                    });
                    return;
                }

                pgf.ui.dialog.wait('stop', stopCallback=function() {
                    for (var i in ids) {
                        var id = ids[i];
                        delete instance.data.cards[id];
                    }

                    localVersion += 1;

                    for (var i in data.data.cards) {
                        var card = data.data.cards[i];
                        instance.data.cards[card.uid] = card;
                    }

                    pgf.ui.dialog.Alert({message: data.data.message,
                                         title: 'Превращение прошло успешно'});

                    Refresh();

                    jQuery(document).trigger(pgf.game.events.CARDS_REFRESHED);
                });
            },
            error: function() {
                    pgf.ui.dialog.wait('stop', stopCallback=function(){
                        pgf.ui.dialog.Error({message: 'Неизвестная ошибка при превращении карт. Пожалуйста, перезагрузите страницу.'});
                    });
            },
            complete: function() {
            }
        });
    };

    this.DeleteCard = function(cardId) {
        localVersion += 1;
        delete instance.data.cards[cardId];
    };

    this.Use = function(cardId) {
        localVersion += 1;
        pgf.ui.dialog.Create({ fromUrl: params.useCardDialog + '?card=' + cardId,
                               OnOpen: function(dialog) {
                                   var cardForm = new pgf.forms.Form(jQuery('.pgf-use-card-form', dialog),
                                                                     { OnSuccess: function(form, data) {
                                                                         jQuery(document).trigger(pgf.game.events.DATA_REFRESH_NEEDED);

                                                                         instance.DeleteCard(cardId);

                                                                         Refresh();

                                                                         jQuery(document).trigger(pgf.game.events.CARDS_REFRESHED);

                                                                         dialog.modal('hide');

                                                                         if (data.data.message) {
                                                                             pgf.ui.dialog.Alert({message: data.data.message,
                                                                                                  title: 'Карта использована',
                                                                                                  OnOk: function(e){instance.GetCards();}});
                                                                         }
                                                                     }});
                               }
                             });
    }

    this.GetCards();
};


pgf.game.NewCardsDialog = function(dialog, newCards) {

    var instance = this;

    var widget = jQuery('.pgf-cards', dialog);

    function Initialize() {
        var cards = pgf.game.widgets.PrepairCardsRenderSequence(newCards);
        pgf.base.RenderTemplateList(widget, cards, pgf.game.widgets.RenderCard, {});

        jQuery('.pgf-no-cards', dialog).toggleClass('pgf-hidden', newCards.length > 0);
    }

    Initialize();
};



pgf.game.CardsStorageDialog = function(dialog, cardsWidget) {

    var instance = this;

    var handWidget = jQuery('.pgf-cards-in-hand', dialog);
    var storageWidget = jQuery('.pgf-cards-in-storage', dialog);

    instance.moveAmount = 1;

    function Initialize() {
        cardsWidget.RenderHand(handWidget);
        cardsWidget.RenderStorage(storageWidget);

        jQuery('.pgf-card-link', handWidget).off().click(function(e){
            e.preventDefault();
            e.stopPropagation();

            var ids = jQuery('.pgf-card-record', e.currentTarget).data('ids');

            var amount = Math.min(instance.moveAmount, ids.length);

            var cardsIds = [];

            for (;;) {
                if (amount <= 0) break;
                amount -= 1;

                cardsIds.push(ids.pop());
            }

            cardsWidget.ToStorage(cardsIds);

            Initialize();
        });

        jQuery('.pgf-card-link', storageWidget).off().click(function(e){
            e.preventDefault();
            e.stopPropagation();

            var ids = jQuery('.pgf-card-record', e.currentTarget).data('ids');

            var cardsIds = [];

            var amount = Math.min(instance.moveAmount, ids.length);
            for (;;) {
                if (amount <= 0) break;
                amount -= 1;

                cardsIds.push(ids.pop());
            }

            cardsWidget.ToHand(cardsIds);

            Initialize();
        });
    }

    jQuery(document).bind(pgf.game.events.CARDS_REFRESHED, function(e, diary){
        Initialize();
    });

    jQuery('.pgf-card-amount-choice a', dialog).off().click(function(e){
        e.preventDefault();
        e.stopPropagation();

        jQuery('.pgf-card-amount-choice li', dialog).toggleClass('active', false);
        jQuery(e.currentTarget).closest('li').toggleClass('active', true);

        instance.moveAmount = jQuery(e.currentTarget).data('amount');
    });

    Initialize();
};


pgf.game.CardsTransformatorDialog = function(dialog, cardsWidget) {

    var instance = this;

    var handWidget = jQuery('.pgf-cards-in-hand', dialog);
    var storageWidget = jQuery('.pgf-cards-in-storage', dialog);
    var transformatorWidget = jQuery('.pgf-cards-in-transformator', dialog);
    var transformButton = jQuery('.pgf-transform-button', dialog)

    function Initialize() {
        cardsWidget.RenderHand(handWidget);
        cardsWidget.RenderStorage(storageWidget);
        cardsWidget.RenderTransformator(transformatorWidget);
        transformButton.toggleClass('pgf-disabled disabled', !cardsWidget.CanTransform())

        jQuery('.pgf-card-link', handWidget).off().click(function(e){
            e.preventDefault();
            e.stopPropagation();

            var ids = jQuery('.pgf-card-record', e.currentTarget).data('ids');

            cardsWidget.ToTransformator(ids.pop());

            Initialize();
        });

        jQuery('.pgf-card-link', storageWidget).off().click(function(e){
            e.preventDefault();
            e.stopPropagation();

            var ids = jQuery('.pgf-card-record', e.currentTarget).data('ids');

            cardsWidget.ToTransformator(ids.pop());

            Initialize();
        });

        jQuery('.pgf-card-link', transformatorWidget).off().click(function(e){
            e.preventDefault();
            e.stopPropagation();

            var ids = jQuery('.pgf-card-record', e.currentTarget).data('ids');

            cardsWidget.FromTransformator(ids.pop());

            Initialize();
        });

        transformButton.off().click(function(e) {
            e.preventDefault();
            e.stopPropagation();

            cardsWidget.Transform();

            Initialize();
        });
    }

    jQuery(document).bind(pgf.game.events.CARDS_REFRESHED, function(e, diary){
        Initialize();
    });

    Initialize();
};


pgf.game.widgets.NEW_CARDS_DIALOG = `
<div class="modal hide">

  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal">×</button>
    <h3 class="pgf-dialog-title dialog-title">Новые карты</h3>
  </div>

  <div class="modal-body">

    <p class="pgf-no-cards pgf-hidden">Вы уже забрали все карты.</p>

    <ul class="pgf-cards pgf-scrollable unstyled" style="max-height: 200px; overflow-y: auto;">
      <li class="pgf-template">
        <a href="#"
           class="pgf-card-link"
           style="font-size: 10pt;">
          <span class="pgf-number" style="color: black;">1</span> x <span class="pgf-card-record"></span>
        </a>
      </li>
    </ul>

    <a href="#" class="btn btn-success" data-dismiss="modal">Забрать</a>

  </div>

</div>
`


pgf.game.widgets.CARDS_STORAGE_DIALOG = `
<div class="modal hide">

  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal">×</button>
    <h3 class="pgf-dialog-title dialog-title">Хранилище карт</h3>
  </div>

  <div class="modal-body">

    <p>Хранилище позволяет отложить в сторону ненужные или редко используемые карты.</p>

    <ul>
      <li>Карты хранилища доступны в интерфейсах рынка и превращения карт, перекладывать их обратно в руку не надо.</li>
      <li>Первыми всегда перекладываются продаваемые карты.</li>
    </ul>

    <ul class="pgf-card-amount-choice nav nav-pills">
      <li class="active"><a data-amount="1" href="#">по 1</a></li>
      <li><a data-amount="5" href="#">по 5</a></li>
      <li><a data-amount="10" href="#">по 10</a></li>
      <li><a data-amount="25" href="#">по 25</a></li>
      <li><a data-amount="50" href="#">по 50</a></li>
      <li><a data-amount="100" href="#">по 100</a></li>
    </ul>

    <table width="100%">
      <thead>
        <tr>
          <th>Карты в руке</th>
          <th width="50%">Карты в хранилище</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="vertical-align: top;">
            <ul class="pgf-cards-in-hand pgf-scrollable unstyled" style="height: 200px; overflow-y: auto;">
              <li class="pgf-template">
                <a href="#"
                   class="pgf-card-link"
                   style="font-size: 10pt;">
                   <span class="pgf-number" style="color: black;">1</span> x <span class="pgf-card-record"></span>
                </a>
              </li>
            </ul>
          </td>
          <td>
            <ul class="pgf-cards-in-storage pgf-scrollable unstyled" style="height: 200px; overflow-y: auto;">
              <li class="pgf-template">
                <a href="#"
                   class="pgf-card-link"
                   style="font-size: 10pt;">
                   <span class="pgf-number" style="color: black;">1</span> x <span class="pgf-card-record"></span>
                </a>
              </li>
            </div>
          </td>
        </tr>
      </tbody>
    </table>

  </div>

</div>
`


pgf.game.widgets.CARDS_TRANSFORMATOR_DIALOG = `
<div class="modal hide">

  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal">×</button>
    <h3 class="pgf-dialog-title dialog-title">Превращение карт</h3>
  </div>

  <div class="modal-body">

    <p>Карты можно превращать друг в друга.</p>

    <ul>
      <li>Одна карта превращается в случайную карту меньшей редкости.</li>
      <li>Две карты одной редкости превращаются в случайную карту той же редкости.</li>
      <li>Три карты одной редкости превращаются в случайную карту большей редкости.</li>
      <li>Часть карт можно превращать по особым правилам, указанным в описании карт.</li>
      <li>Если всеми превращаемыми картами можно торговать на рынке, то и новой картой можно будет торговать на рынке.</li>
      <li>Первыми в обмен отправляются продаваемые карты.</li>
      <li>Первыми из обмена забираются непродаваемые карты.</li>
      <li>Если у вас много одинаковых карт, использование хранилища поможет удобнее их объединять.</li>
    </ul>

    <table width="100%">
      <thead>
        <tr>
          <th colspan="2">Карты для превращения</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td width="80%">
            <ul class="pgf-cards-in-transformator pgf-scrollable unstyled" style="height: 60px; overflow-y: auto;">
              <li class="pgf-template">
                <a href="#"
                   class="pgf-card-link"
                   style="font-size: 10pt;">
                   <span class="pgf-number" style="color: black;">1</span> x <span class="pgf-card-record"></span>
                </a>
              </li>
            </div>
          </td>
          <td style="vertical-align: middle;">
            <button class="pgf-transform-button pgf-disabled disabled btn btn-large btn-success" type="button">Превратить</button>
          </td>
        </tr>
      </tbody>
    </table>


    <table width="100%">
      <thead>
        <tr>
          <th>Карты в руке</th>
          <th width="50%">Карты в хранилище</th>
        </tr>

      </thead>
        <tr>
          <td style="vertical-align: top;">
            <ul class="pgf-cards-in-hand pgf-scrollable unstyled" style="height: 200px; overflow-y: auto;">
              <li class="pgf-template">
                <a href="#"
                   class="pgf-card-link"
                   style="font-size: 10pt;">
                   <span class="pgf-number" style="color: black;">1</span> x <span class="pgf-card-record"></span>
                </a>
              </li>
            </ul>
          </td>
          <td style="vertical-align: top;">
            <ul class="pgf-cards-in-storage pgf-scrollable unstyled" style="height: 200px; overflow-y: auto;">
              <li class="pgf-template">
                <a href="#"
                   class="pgf-card-link"
                   style="font-size: 10pt;">
                   <span class="pgf-number" style="color: black;">1</span> x <span class="pgf-card-record"></span>
                </a>
              </li>
            </ul>
          </td>
        </tr>
      </tbody>
    </table>

  </div>

</div>
`
