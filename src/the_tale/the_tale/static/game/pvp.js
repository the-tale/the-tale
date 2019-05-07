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


pgf.game.events.PVP_REFRESHED = 'pgf-pvp-refreshed';


pgf.game.widgets.RenderBattleRequest = function(index, item, element) {

    var hero = widgets.heroes.CurrentHero();

    jQuery('.pgf-arena-initiator-level', element).text(item.account.hero.level);

    var clanElement = jQuery('.pgf-arena-battle-owner-clan', element);

    clanElement.toggleClass('pgf-hidden', !item.clan);

    if (item.clan) {
        clanElement.text('['+item.clan.abbr+']').attr('href', clanElement.attr('href').replace('__clan_id__', item.clan.id));
    }

    var ownerElement = jQuery('.pgf-arena-battle-owner', element);

    ownerElement.text(item.account.name).attr('href', ownerElement.attr('href').replace('__account_id__', item.account.id));

    var heroElement = jQuery('.pgf-arena-battle-hero', element);

    heroElement.attr('href', heroElement.attr('href').replace('__hero_id__', item.account.id));;

    jQuery('.pgf-arena-battle-hero-physic-power', element).text(item.account.hero.power[0]);
    jQuery('.pgf-arena-battle-hero-magic-power', element).text(item.account.hero.power[1]);

    if (hero) {
        jQuery('.pgf-arena-accept-battle', element).toggleClass('pgf-hidden', (item.account.id == hero.id));
        jQuery('.pgf-arena-accept-own-battle', element).toggleClass('pgf-hidden', (item.account.id != hero.id));
    }

    var requestId = item.request.id;

    jQuery('.pgf-arena-accept-battle', element).off().click(function(e) {
        e.preventDefault();
        e.stopPropagation();

        widgets.pvp.AcceptArenaBattle(requestId);
    });
};


pgf.game.widgets.PvP = function (params) {

    var instance = this;

    instance.data = {arenaBattleRequests: [],
                     activeBotBattles: [],
                     activeArenaBattles: [],
                     accounts: {},
                     clans: {}};

    var localVersion = 0;
    var refreshInterval = undefined;
    var refreshTimer = undefined;

    instance.SetRefreshInterval = function(intervalTime) {
        refreshInterval = intervalTime;
        refreshTimer = setInterval(function(e){
            instance.GetInfo();
        }, refreshInterval);
    };

    this.RefreshInfo = function(data) {
        instance.data.arenaBattleRequests = data.arena_battle_requests;
        instance.data.activeBotBattles = data.active_battles;
        instance.data.activeArenaBattles = data.active_arena_battles;
        instance.data.accounts = data.accounts;
        instance.data.clans = data.clans;

        jQuery(document).trigger(pgf.game.events.PVP_REFRESHED);
    };

    this.GetInfo = function() {

        var requestedVersion = localVersion + 1;

        jQuery.ajax({
            dataType: 'json',
            type: 'get',
            url: params.info,

            success: function(data, request, status) {

                if (requestedVersion <= localVersion) {
                    instance.GetCards();
                    return;
                }

                localVersion = requestedVersion;

                instance.RefreshInfo(data.data.info);
            },
            error: function() {
            },
            complete: function() {
            }
        });
    };

    this.CallToArena = function() {
        pgf.forms.Post({ action: params.callToArena,
                         OnSuccess: function(data){
                             instance.RefreshInfo(data.data.info);
                         }
                       });
    }

    this.LeaveArena = function() {
        pgf.forms.Post({ action: params.leaveArena,
                         OnSuccess: function(data){
                             instance.RefreshInfo(data.data.info);
                         }
                       });
    }

    this.AcceptArenaBattle = function(requestId) {
        pgf.forms.Post({ action: params.acceptArenaBattle + '&battle_request_id=' + requestId,
                         OnSuccess: function(data){
                             location.href = params.pvpPage;
                         }
                       });
    }

    this.CreateArenaBotBattle = function(requestId) {
        pgf.forms.Post({ action: params.createArenaBotBattle,
                         OnSuccess: function(data){
                             location.href = params.pvpPage;
                         }
                       });
    }

    this.BattlesAmount = function() {
        return instance.data.arenaBattleRequests.length;
    };

    this.HasBattleRequests = function() {
        return instance.data.arenaBattleRequests.length > 0;
    };

    this.HasRequestFromAccount = function(accountId) {
        for (var i in instance.data.arenaBattleRequests) {
            if (instance.data.arenaBattleRequests[i].initiator_id == accountId) {
                return true;
            }
        }

        return false;
    };

    this.RenderArenaBattleRequests = function(widget) {
        var requests = [];

        for (var i in instance.data.arenaBattleRequests) {
            var request = instance.data.arenaBattleRequests[i];
            var account = instance.data.accounts[request.initiator_id];
            requests.push({'request': request,
                           'account': instance.data.accounts[request.initiator_id],
                           'clan': instance.data.clans[account.clan]});
        }

        requests.sort(function(a, b){
            if (a.request.updated_at < b.request.updated_at) return 1;
            if (a.request.updated_at > b.request.updated_at) return -1;
            if (a.request.initiator_id < b.request.initiator_id) return -1;
            if (a.request.initiator_id > b.request.initiator_id) return 1;
            return 0;
        });

        pgf.base.RenderTemplateList(widget, requests, pgf.game.widgets.RenderBattleRequest, {});
    };


    this.GetInfo();
};
