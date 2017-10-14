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


pgf.game.events.MARKET_REFRESHED = 'pgs-market-refreshed';

pgf.game._ShopCompareCardNames = function(a, b) {
    if (a.name.toLowerCase() < b.name.toLowerCase()) return -1;
    if (a.name.toLowerCase() > b.name.toLowerCase()) return 1;
    return 0;
};

pgf.game.SHOP_CARDS_COMPARATORS = {
    name_up: function(a, b) {
        return -pgf.game._ShopCompareCardNames(a, b);
    },

    name_down: function(a, b) {
        return pgf.game._ShopCompareCardNames(a, b);
    },

    rarity_up: function(a, b) {
        if (a.rarity > b.rarity) return -1;
        if (a.rarity < b.rarity) return 1;
        return pgf.game._ShopCompareCardNames(a, b);
    },

    rarity_down: function(a, b) {
        if (a.rarity < b.rarity) return -1;
        if (a.rarity > b.rarity) return 1;
        return pgf.game._ShopCompareCardNames(a, b);
    },

    in_deck_up: function(a, b) {
        if (a.inDeckToTrade > b.inDeckToTrade) return -1;
        if (a.inDeckToTrade < b.inDeckToTrade) return 1;
        return pgf.game._ShopCompareCardNames(a, b);
    },

    in_deck_down: function(a, b) {
        if (a.inDeckToTrade < b.inDeckToTrade) return -1;
        if (a.inDeckToTrade > b.inDeckToTrade) return 1;
        return pgf.game._ShopCompareCardNames(a, b);
    },

    owner_sell_number_up: function(a, b) {
        if (a.ownerSellNumber > b.ownerSellNumber) return -1;
        if (a.ownerSellNumber < b.ownerSellNumber) return 1;
        return pgf.game._ShopCompareCardNames(a, b);
    },

    owner_sell_number_down: function(a, b) {
        if (a.ownerSellNumber < b.ownerSellNumber) return -1;
        if (a.ownerSellNumber > b.ownerSellNumber) return 1;
        return pgf.game._ShopCompareCardNames(a, b);
    },

    in_trade_up: function(a, b) {
        if (a.inTrade > b.inTrade) return -1;
        if (a.inTrade < b.inTrade) return 1;
        return pgf.game._ShopCompareCardNames(a, b);
    },

    in_trade_down: function(a, b) {
        if (a.inTrade < b.inTrade) return -1;
        if (a.inTrade > b.inTrade) return 1;
        return pgf.game._ShopCompareCardNames(a, b);
    },

    min_price_up: function(a, b) {
        var x = a.minPrice == undefined ? 0 : a.minPrice;
        var y = b.minPrice == undefined ? 0 : b.minPrice;

        if (x > y) return -1;
        if (x < y) return 1;

        return pgf.game._ShopCompareCardNames(a, b);
    },

    min_price_down: function(a, b) {
        var x = a.minPrice == undefined ? 0 : a.minPrice;
        var y = b.minPrice == undefined ? 0 : b.minPrice;

        if (x < y) return -1;
        if (x > y) return 1;

        return pgf.game._ShopCompareCardNames(a, b);
    },

    max_price_up: function(a, b) {
        var x = a.maxPrice == undefined ? 0 : a.maxPrice;
        var y = b.maxPrice == undefined ? 0 : b.maxPrice;

        if (x > y) return -1;
        if (x < y) return 1;

        return pgf.game._ShopCompareCardNames(a, b);
    },

    max_price_down: function(a, b) {
        var x = a.maxPrice == undefined ? 0 : a.maxPrice;
        var y = b.maxPrice == undefined ? 0 : b.maxPrice;

        if (x < y) return -1;
        if (x > y) return 1;

        return pgf.game._ShopCompareCardNames(a, b);
    }
};

pgf.game.ShopCardsBrowser = function(params) {

    var instance = this;

    instance.params = params;

    var container = params.container;

    var filterContainer = jQuery('.pgf-cards-filter', container);
    var rarityFilter = jQuery('.pgf-cards-rarity', filterContainer);

    var listContainer = jQuery('.pgf-cards-list', container);

    var resetButton = jQuery('.pgf-reset-filter', container);
    var nameFilterContainer = jQuery('.pgf-cards-name-filter', container);
    var rarityCurrentFilterValue = jQuery('.pgf-card-rarity-filter-current-rarity', container);

    var userCards = params.userCards

    var sortInfo = {parameter: pgf.base.settings.get('market_sort_parameter', 'name'),
                    direction: pgf.base.settings.get('market_sort_direction', 'down')};

    var ALL_RARITY = {name: 'ALL', text: 'любая'};

    var nameFilterInfo = '';
    var rarityFilterInfo = ALL_RARITY.name;

    instance.data = {cards: [],
                     market: [],
                     balance: 0};

    var firstRequest = true;

    this.GetInfo = function(callback) {
        var oldMarket = instance.data.market;

        jQuery.ajax({
            dataType: 'json',
            type: 'get',
            url: params.infoUrl,

            success: function(data, request, status) {
                instance.data.market = data.data.info;

                var dataChanged = !(JSON.stringify(oldMarket) == JSON.stringify(instance.data.market));

                firstRequest = false;

                if (callback) {
                    callback();
                }

                instance.data.balance = data.data.account_balance;

                jQuery('.pgf-account-balance').text(instance.data.balance);

                if (dataChanged || firstRequest) {
                    jQuery(document).trigger(pgf.game.events.MARKET_REFRESHED);
                }
            },
            error: function() {
            },
            complete: function() {
            }
        });
    };

    function RenderRarityFilterRecord(index, rarity, element) {
        jQuery('.pgf-rarity-filter-record', element).
            toggleClass(rarity.name.toLowerCase()+'-card-label', true).
            data('filter-rarity', rarity.name).
            text(rarity.text);
    };

    function InitializeRarityFilter() {
        rarities = [];
        for (var i in pgf.game.constants.CARD_RARITY) {
            rarities[i] = pgf.game.constants.CARD_RARITY[i];
        }
        rarities.unshift(ALL_RARITY);

        pgf.base.RenderTemplateList(jQuery('.pgf-cards-rarity-filter-list', rarityFilter),
                                    rarities,
                                    RenderRarityFilterRecord,
                                    {});
    };

    function RefreshSortUI() {
        jQuery('.pgf-sort-up', container).toggleClass('pgf-hidden', true);
        jQuery('.pgf-sort-down', container).toggleClass('pgf-hidden', true);

        jQuery('.pgf-sort-'+sortInfo.parameter+' .pgf-sort-'+sortInfo.direction).toggleClass('pgf-hidden', false)
    };

    function RenderCardRecord(index, card, element) {
        var rarityClass = pgf.game.constants.CARD_RARITY[card.rarity].name.toLowerCase()+'-card-label';

        jQuery('.pgf-card-rarity', element).toggleClass(rarityClass, true);

        jQuery('.pgf-card-name', element).toggleClass(rarityClass, true).text(card.name);

        jQuery('.pgf-cards-in-deck-to-trade', element).text(card.inDeckToTrade);
        jQuery('.pgf-cards-in-deck-total', element).text(card.inDeckTotal);
        jQuery('.pgf-owner-sell-number', element).text(card.ownerSellNumber);
        jQuery('.pgf-cards-in-trade', element).text(card.inTrade);
        jQuery('.pgf-card-min-price', element).text(card.minPrice ? card.minPrice : "—");
        jQuery('.pgf-card-max-price', element).text(card.maxPrice ? card.maxPrice : "—");

        jQuery('.pgf-operations-button', element).data('card-type', card.full_type);

        var tooltipClass = 'pgf-card-tooltip';
        var tooltip = pgf.game.widgets.CreateCardTooltip(card, tooltipClass);

        var tooltipElement = jQuery('.pgf-card-name', element);

        tooltipElement.data('placement', 'right');

        pgf.base.UpdateElementTooltip(tooltipElement, tooltip, tooltipClass, pgf.game.widgets.GetCardsTooltipArgs());
    };

    function RefreshTotal(cards) {
        var inDeckToTrade = 0;
        var inDeckTotal = 0;
        var inTradeTotal = 0;
        for (var i in cards) {
            inDeckToTrade += cards[i].inDeckToTrade;
            inDeckTotal += cards[i].inDeckTotal;
            inTradeTotal += cards[i].inTrade;
        }
        jQuery('.pgf-cards-number-in-deck-to-trade', container).text(inDeckToTrade);
        jQuery('.pgf-cards-number-in-deck-total', container).text(inDeckTotal);
        jQuery('.pgf-cards-number-in-trade', container).text(inTradeTotal);
    };

    function RefreshResetButton() {
        var isFilterActive = nameFilterInfo || (rarityFilterInfo !== ALL_RARITY.name);

        if (!isFilterActive) {
            resetButton.toggleClass('disabled', true).text("видны все карты");
        }
        else {
            resetButton.toggleClass('disabled', false).text("сбросить фильтр");
        }
    };

    function InitializeList() {
        var cards = pgf.game.ShopUserDeckPreprocessor(userCards.data.cards, instance.data.market);

        var nameFilter = nameFilterInfo.toLowerCase();

        cards = cards.filter(function(card){return card.name.toLowerCase().includes(nameFilter);})

        if (rarityFilterInfo != ALL_RARITY.name) {
            cards = cards.filter(function(card){return pgf.game.constants.CARD_RARITY[card.rarity].name == rarityFilterInfo;})
        }

        cards.sort(pgf.game.SHOP_CARDS_COMPARATORS[sortInfo.parameter+'_'+sortInfo.direction]);

        instance.data.cards = cards;

        pgf.base.RenderTemplateList(listContainer,
                                    cards,
                                    RenderCardRecord,
                                    {});

        RefreshSortUI();
        RefreshTotal(cards);
        RefreshResetButton();

        jQuery('.pgf-operations-button', listContainer).click(function(e){
            var cardType = jQuery(e.currentTarget).data('card-type');

            pgf.game.OperationsDialog(instance, cardType);
        });
    };

    function Refresh() {
        InitializeList();
    };

    this.GetCardByType = function(type) {
        for (var i in instance.data.cards) {
            var card = instance.data.cards[i];
            if (card.full_type == type) {
                return card;
            }
        }
    };

    jQuery(document).bind(pgf.game.events.CARDS_REFRESHED, function(e, diary){
        Refresh();
    });

    jQuery(document).bind(pgf.game.events.MARKET_REFRESHED, function(e, diary){
        Refresh();
    });

    nameFilterContainer.on('input', function(e){
        nameFilterInfo = jQuery(e.currentTarget).val();
        Refresh();
    })

    resetButton.click(function(){
        nameFilterInfo = '';
        nameFilterContainer.val('');

        rarityFilterInfo = ALL_RARITY.name;
        rarityCurrentFilterValue.text(ALL_RARITY.text);

        Refresh();
    });

    InitializeRarityFilter();

    jQuery('.pgf-rarity-filter-record', container).click(function(e){
        var record = jQuery(e.currentTarget);

        rarityFilterInfo = record.data('filter-rarity');

        var rarityClass = rarityFilterInfo.toLowerCase()+'-card-label';

        var nameElement = '<span class="'+rarityClass+'">' + record.text() + '</span>';

        rarityCurrentFilterValue.html(nameElement);

        Refresh();
    });

    jQuery('.pgf-cards-list-header', container).click(function(e){
        e.preventDefault();
        e.stopPropagation();

        var parameter = jQuery(e.currentTarget).data('sort-parameter');
        var defaultDirection = jQuery(e.currentTarget).data('sort-default-direction');

        if (!parameter) {
            return;
        };

        if (sortInfo.parameter != parameter) {
            sortInfo.parameter = parameter;
            sortInfo.direction = defaultDirection;
        }
        else {
            sortInfo.direction = sortInfo.direction == 'down' ? 'up': 'down';
        }

        pgf.base.settings.set('market_sort_parameter', sortInfo.parameter);
        pgf.base.settings.set('market_sort_direction', sortInfo.direction);

        Refresh();
    });

    instance.GetInfo();
};

pgf.game.ShopUserDeckPreprocessor = function(cardInfos, marketInfo) {
    var cardsByType = {};

    for (var i in cardInfos) {
        var cardInfo = cardInfos[i];

        if (!(cardInfo.name in cardsByType)) {
            cardsByType[cardInfo.name] = {inDeckToTrade: 0,
                                          inDeckTotal: 0,
                                          inTrade: 0,
                                          type: cardInfo.type,
                                          full_type: cardInfo.full_type,
                                          rarity: cardInfo.rarity,
                                          ids: [],
                                          minPrice: undefined,
                                          maxPrice: undefined,
                                          ownerSellNumber: 0,
                                          name: cardInfo.name};
        }

        if (cardInfo.auction) {
            cardsByType[cardInfo.name].inDeckTotal += 1;
            cardsByType[cardInfo.name].inDeckToTrade += 1;
            cardsByType[cardInfo.name].ids.push(cardInfo.uid);
        }
        else {
            cardsByType[cardInfo.name].inDeckTotal += 1;
        }
    }

    for (var i in marketInfo) {
        var cardInfo = marketInfo[i];

        if (!(cardInfo.name in cardsByType)) {
            cardsByType[cardInfo.name] = {inDeckToTrade: 0,
                                          inDeckTotal: 0,
                                          inTrade: 0,
                                          type: cardInfo.type,
                                          full_type: cardInfo.full_type,
                                          rarity: pgf.game.constants.CARD_TYPE[cardInfo.type].rarity,
                                          ids: [],
                                          minPrice: undefined,
                                          maxPrice: undefined,
                                          ownerSellNumber: 0,
                                          name: cardInfo.name};
        }

        cardsByType[cardInfo.name].ownerSellNumber = cardInfo.owner_sell_number;
        cardsByType[cardInfo.name].inTrade += cardInfo.sell_number;
        cardsByType[cardInfo.name].minPrice = cardInfo.min_sell_price;
        cardsByType[cardInfo.name].maxPrice = cardInfo.max_sell_price;
    }

    var cards = [];

    for (var i in cardsByType) {
        cards.push(cardsByType[i]);
    }

    cards.sort(pgf.game.widgets.CardsComparator);

    return cards
};


pgf.game.OperationsDialog = function(shopCardsBrowser, cardType) {

    var instance = this;

    instance.dialog = undefined;
    instance.prices = undefined;
    instance.ownerPrices = undefined;

    function RefreshPrices(prices, ownerPrices) {
        jQuery('.pgf-has-no-prices', instance.dialog).toggleClass('pgf-hidden', !jQuery.isEmptyObject(prices));
        jQuery('.pgf-has-prices', instance.dialog).toggleClass('pgf-hidden', jQuery.isEmptyObject(prices));

        var orderedPrices = [];

        for (var price in prices) {
            orderedPrices.push([parseInt(price),
                                prices[price],
                                ownerPrices[price] ? ownerPrices[price] : 0]);
        }
        orderedPrices.sort(function(a, b){return a[0]-b[0];});

        if (orderedPrices.length > 0) {
            jQuery('.pgf-min-buy-price', instance.dialog).text(orderedPrices[0][0]);
            jQuery('.pgf-close-sell-lots', instance.dialog).data('min-price', orderedPrices[0][0]);
            jQuery('.pgf-account-balance').text(shopCardsBrowser.data.balance);
        }
        jQuery('.pgf-buy-block', instance.dialog).toggleClass('pgf-hidden', (jQuery.isEmptyObject(prices) || (orderedPrices[0][2] > 0) || !(shopCardsBrowser.data.balance > orderedPrices[0][0])));
        jQuery('.pgf-buy-block-has-card-error', instance.dialog).toggleClass('pgf-hidden', (jQuery.isEmptyObject(prices) || (orderedPrices[0][2] == 0)));
        jQuery('.pgf-buy-block-no-money-error', instance.dialog).toggleClass('pgf-hidden', ((orderedPrices.length == 0) || (shopCardsBrowser.data.balance > orderedPrices[0][0])))

        pgf.base.RenderTemplateList(jQuery('.pgf-prices-container', instance.dialog),
                                    orderedPrices,
                                    RenderPriceRecord,
                                    {});

    }

    function LoadPrices(callback) {
        jQuery.ajax({
            dataType: 'json',
            type: 'get',
            data: {item_type: cardType},
            url: shopCardsBrowser.params.itemTypePricesUrl,

            success: function(data, request, status) {

                instance.prices = data.data.prices;
                instance.ownerPrices = data.data.owner_prices;

                if (instance.dialog) {
                    RefreshPrices(instance.prices, instance.ownerPrices);
                }

                if (callback) {
                    callback();
                }
            },
            error: function() {
            },
            complete: function() {
            }});
    }

    function UpdateCalculations(value, commissionPercents) {
        var commission = Math.floor(value * commissionPercents);

        if (commission == 0) {
            commission = 1;
        }

        jQuery('.pgf-seller-income', instance.dialog).text(value - commission);
        jQuery('.pgf-seller-commission', instance.dialog).text(commission);
    }

    function ReturnOwnCardCallback(e) {
        e.preventDefault();
        e.stopPropagation();

        var element = jQuery(e.currentTarget);

        var price = element.data('price');

        data = new FormData();

        data.append('price', price);
        data.append('item_type', cardType);

        pgf.ui.dialog.wait('start');

        function OnSuccess(data, request, status) {
            if (data.status == 'error') {
                pgf.ui.dialog.wait('stop', stopCallback=function(){
                    pgf.ui.dialog.Error({message: data.error});
                });
                return;
            }

            shopCardsBrowser.params.userCards.GetCards();
            shopCardsBrowser.GetInfo(function(){
                LoadPrices(function(){
                    pgf.ui.dialog.wait('stop');
                });
            });
        }

        jQuery.ajax({dataType: 'json',
                     type: 'post',
                     url: shopCardsBrowser.params.cancelSellLotUrl,
                     data: data,
                     contentType: false,
                     processData: false,
                     success: OnSuccess,
                     error: function() {
                         pgf.ui.dialog.wait('stop', stopCallback=function(){
                             pgf.ui.dialog.Error({message: 'Неизвестная ошибка. Пожалуйста, перезагрузите страницу.'});
                         });
                     },
                     complete: function() {}});
    }

    function RenderPriceRecord(index, price, element) {
        jQuery(".pgf-market-price", element).text(price[0]);
        jQuery(".pgf-market-count", element).text(price[1]);
        jQuery(".pgf-own-market-count", element).text(price[2] ? price[2] : '—');
        jQuery(".pgf-return-own-card", element)
            .toggleClass('pgf-hidden', (price[2]==0))
            .data('price', price[0]);

        jQuery(".pgf-return-own-card", element).click(ReturnOwnCardCallback);
    }

    function Refresh() {
        var card = shopCardsBrowser.GetCardByType(cardType);

        jQuery('#pgf_id_cards_number', instance.dialog).attr('max', card.inDeckToTrade);
        jQuery('.pgf-card-min-price', instance.dialog).text(shopCardsBrowser.params.minSellPrice);
        jQuery('.pgf-max-cards-to-sell', instance.dialog).text(card.inDeckToTrade);

        jQuery('.pgf-no-cards-to-sell-block', instance.dialog).toggleClass('pgf-hidden', (0 < card.inDeckToTrade));
        jQuery('.pgf-sell-cards-block', instance.dialog).toggleClass('pgf-hidden', !(0 < card.inDeckToTrade));
    }

    function Initialize() {
        var card = shopCardsBrowser.GetCardByType(cardType);

        var rarityClass = pgf.game.constants.CARD_RARITY[card.rarity].name.toLowerCase()+'-card-label';

        jQuery('.pgf-card-description', instance.dialog).text(pgf.game.constants.CARD_TYPE[card.type].description);

        jQuery('.pgf-card-name', instance.dialog)
            .text(card.name[0].toUpperCase() + card.name.slice(1, card.name.length))
            .toggleClass(rarityClass, true);

        jQuery('.pgf-cookies-image', instance.dialog).attr("src", shopCardsBrowser.params.cookiesImage);

        jQuery('#pgf_id_cards_price', instance.dialog).attr('min', shopCardsBrowser.params.minSellPrice);

        jQuery('.pgf-market-commission', instance.dialog).text(Math.ceil(shopCardsBrowser.params.sellComission*100));

        UpdateCalculations(shopCardsBrowser.params.minSellPrice, shopCardsBrowser.params.sellComission);

        jQuery('#pgf_id_cards_price', instance.dialog).on('input', function(e){
            var value = jQuery(e.currentTarget).val();
            UpdateCalculations(value, shopCardsBrowser.params.sellComission);
        });

        Refresh();

        jQuery('.pgf-create-sell-lots', instance.dialog).click(function(e){
            var price = jQuery('#pgf_id_cards_price', instance.dialog).val();
            var number = jQuery('#pgf_id_cards_number', instance.dialog).val();

            var card = shopCardsBrowser.GetCardByType(cardType);

            var ids = card.ids.slice(0, number);

            data = new FormData();

            for (var i in ids) {
                data.append('card', ids[i]);
            }

            data.append('price', price);

            pgf.ui.dialog.wait('start');

            jQuery.ajax({
                dataType: 'json',
                type: 'post',
                url: shopCardsBrowser.params.createSellLotUrl,
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

                    shopCardsBrowser.params.userCards.GetCards();
                    shopCardsBrowser.GetInfo(function(){
                        LoadPrices(function(){
                            pgf.ui.dialog.wait('stop');
                        });
                    });
                },
                error: function() {
                    pgf.ui.dialog.wait('stop', stopCallback=function(){
                        pgf.ui.dialog.Error({message: 'Неизвестная ошибка. Пожалуйста, перезагрузите страницу.'});
                    });
                },
                complete: function() {
                }
            });
        });

        jQuery('.pgf-close-sell-lots', instance.dialog).click(function(e){
            var price = jQuery('.pgf-close-sell-lots', instance.dialog).data('min-price');

            if (shopCardsBrowser.data.balance < price) {
                return;
            }

            data = new FormData();

            data.append('price', price);
            data.append('item_type', cardType);

            pgf.ui.dialog.wait('start');

            function OnSuccess(data, request, status) {
                if (data.status == 'error') {
                    pgf.ui.dialog.wait('stop', stopCallback=function(){
                        pgf.ui.dialog.Error({message: data.error});
                    });
                    return;
                }

                if (data.status == 'processing') {
                    setTimeout(function() {
                        jQuery.ajax({dataType: 'json',
                                     type: 'get',
                                     url: data.status_url,
                                     success: OnSuccess,
                                     error: OnError,
                                     complete: function() {}});
                    }, 0.5*1000)
                    return;
                }

                shopCardsBrowser.params.userCards.GetCards();
                shopCardsBrowser.GetInfo(function(){
                    LoadPrices(function(){
                        pgf.ui.dialog.wait('stop');
                    });
                });
            }

            function OnError() {
                pgf.ui.dialog.wait('stop', stopCallback=function(){
                    pgf.ui.dialog.Error({message: 'Неизвестная ошибка при выставлении карт на продажу. Пожалуйста, перезагрузите страницу.'});
                });
            }

            jQuery.ajax({dataType: 'json',
                         type: 'post',
                         url: shopCardsBrowser.params.closeSellLotUrl,
                         data: data,
                         contentType: false,
                         processData: false,

                         success: OnSuccess,
                         error: OnError,
                         complete: function() {}});
        });
    }

    LoadPrices(function(){
        pgf.ui.dialog.Create({ fromString: pgf.game.CARDS_OPERATIONS_DIALOG,
                               OnOpen: function(dialog) {
                                   instance.dialog = dialog;

                                   Initialize();

                                   RefreshPrices(instance.prices, instance.ownerPrices);

                                   jQuery(document).bind(pgf.game.events.CARDS_REFRESHED, function(e, diary){
                                       Refresh();
                                   });

                                   jQuery(document).bind(pgf.game.events.MARKET_REFRESHED, function(e, diary){
                                       Refresh();
                                   });
                               }
                             });
    });
};


pgf.game.CARDS_OPERATIONS_DIALOG = `
<div class="modal hide">

  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal">×</button>
    <h3 class="pgf-dialog-title dialog-title">
      <span class="pgf-card-name"></span>
    </h3>
  </div>

  <div class="modal-body tabbable">

    <p class="pgf-card-description alert alert-info"></p>

    <ul class="nav nav-tabs">
      <li class="active"><a href="#pgf-buy-panel" class="pgf-buy-panel-button" data-toggle="tab">Купить</a></li>
      <li><a href="#pgf-sell-panel" class="pgf-sell-panel-button" data-toggle="tab">Продать</a></li>
    </ul>

    <div class="tab-content">
      <div class="tab-pane active" id="pgf-buy-panel">
        <p class="pgf-buy-block">
          <a class="btn btn-success pgf-close-sell-lots">Купить</a> 1 карту за <span class="pgf-min-buy-price"></span>
          <img class="pgf-cookies-image" style="vertical-align: middle;" rel="tooltip" title="печеньки"></img>
          у вас есть <span class="pgf-account-balance"></span>
          <img class="pgf-cookies-image" style="vertical-align: middle;" rel="tooltip" title="печеньки"></img>
        </p>

        <p class="pgf-buy-block-no-money-error alert alert-info">
          У вас недостаточно печенек, чтобы купить карту.
        </p>

        <p class="pgf-buy-block-has-card-error alert alert-info">
          Вы продаёте свою карту по минимальной цене. Вместо покупки новой карты вы можете отозвать её с рынка.
        </p>

      </div>

      <div class="tab-pane" id="pgf-sell-panel">

        <p>
          Цена продажи должна быть не меньше <span class="pgf-card-min-price"></span>
          <img class="pgf-cookies-image" style="vertical-align: middle;" rel="tooltip" title="печеньки"></img>
        </p>

        <p>
          Комиссия взимается с каждой успешной торговой операции и составляет <span class="pgf-market-commission"></span>%.
        </p>

        <div class="pgf-sell-cards-block">
          <p>
            <label for="pgf_id_cards_price" style="display: inline-block;">Цена</label>
            <input id="pgf_id_cards_price" class="input-small" type="number" value="10" required="" min="10" style="margin: 0;"/>
              <img class="pgf-cookies-image" style="vertical-align: middle;" rel="tooltip" title="печеньки"></img>
            &nbsp;
            x
            &nbsp;
            <input id="pgf_id_cards_number" class="input-small" type="number" value="1" required="" min="1" max="" style="margin: 0;"/>
            <label for="pgf_id_cards_number" style="display: inline-block;">штук</label>
            из
            <span class="pgf-max-cards-to-sell"></span>
          </p>

          <p>
            Ваш доход: <span class="pgf-seller-income"></span>
            <img class="pgf-cookies-image" style="vertical-align: middle;" rel="tooltip" title="печеньки"></img>
            с одной карты
          </p>
          <p>
            Комиссия: <span class="pgf-seller-commission"></span>
            <img class="pgf-cookies-image" style="vertical-align: middle;" rel="tooltip" title="печеньки"></img>
            с одной карты
          </p>

          <p>
            <a class="btn btn-success pgf-create-sell-lots">Продать</a>
          </p>
        </div>

        <div class="pgf-no-cards-to-sell-block">
          <p class="alert alert-info">У вас нет карт для продажи.</p>
        </div>



      </div>
    </div>

    <div class="pgf-has-prices">
      <h4>Сейчас в продаже</h4>

        <table class="table" style="margin: 0;">
          <thead>
            <tr>
              <th width="100px">Цена</th>
              <th width="100px">Количество</th>
              <th>Ваши карты</th>
            </tr>
          </thead>
        </table>

        <div class="pgf-scrollable" style="overflow-y: auto; max-height: 200px;">
          <table class="table">
            <tbody class="pgf-prices-container">
              <tr class="pgf-template">
                <td width="100px">
                  <span class="pgf-market-price"></span>
                  <img class="pgf-cookies-image" style="vertical-align: middle;" rel="tooltip" title="печеньки"></img>
                </td>
                <td width="100px" class="pgf-market-count"></td>
                <td>
                  <span class="pgf-own-market-count"></span>
                  <a href="#" class="pgf-return-own-card">забрать карту</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

    </div>

    <div class="pgf-has-no-prices">
      <p class="alert alert-info">
        Этих карт сейчас нет в продаже.
      </p>
    </div>

  </div>
</div>
`
