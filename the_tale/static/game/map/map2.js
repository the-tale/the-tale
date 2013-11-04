if (!window.pgf) {
    pgf = {};
}

if (!pgf.game) {
    pgf.game = {};
}

if (!pgf.game.map) {
    pgf.game.map = {};
}

if (!pgf.game.resources) {
    pgf.game.resources = {};
}

if (!pgf.game.resources.events) {
    pgf.game.resources.events = {};
}

if (!pgf.game.map.events) {
    pgf.game.map.events = {};
}

pgf.game.resources.events.SPRITES_LOADED = 'pgf-game-resources-sprites-loaded';
pgf.game.map.events.DATA_UPDATED = 'pgf-game-map-data-updated';

pgf.game.resources.Image = function(sourceImage, src, x, y, w, h) {

    this.src = src;
    this.x = x;
    this.y = y;
    this.w = w;
    this.h = h;

    var image = document.createElement('canvas');
    image.width = w;
    image.height = h;

    var _tmpContext = image.getContext('2d');
    _tmpContext.drawImage(sourceImage,
                          x, y, w, h,
                          0, 0, w, h);


    this.Draw = function(context, x, y) {
        context.drawImage(image, x, y);
    };
};

pgf.game.resources.ImageManager =  function(spritesSettins, params) {

    var spritesSources = {};

    var loadedSources = 0;
    var totalSources = 0;

    var initializedSprites = 0;
    var totalSprites = 0;

    var sprites = {};

    function InitializeSourceSprites(properties) {
        for( spriteName in spritesSettins) {

            if (typeof(spritesSettins[spriteName])=='string') continue;

            if (spritesSettins[spriteName].src == properties.src) {
                var data = spritesSettins[spriteName];
                sprites[spriteName] = new pgf.game.resources.Image(properties.image, params.staticUrl+properties.src, data.x, data.y, data.w, data.h);
                initializedSprites += 1;
            }
        }

        if (initializedSprites == totalSprites) {
            jQuery(document).trigger(pgf.game.resources.events.SPRITES_LOADED);
        }
    }

    for(spriteName in spritesSettins) {
        var data = spritesSettins[spriteName];

        if (typeof(data)=='string') {
            sprites[spriteName] = data; // store link to real sprite
            continue;
        }

        totalSprites += 1;

        if (spritesSources[data.src] == undefined) {
            spritesSources[data.src] = true;
            totalSources += 1;

            (function() {
                var image = new Image();
                var sourceProperties = { loaded: false,
                                         image: image,
                                         src: data.src,
                                         error: undefined };

                image.onload = function(e) {
                    sourceProperties.loaded = true;
                    loadedSources += 1;
                    InitializeSourceSprites(sourceProperties);
                };
                image.src = params.staticUrl + data.src;
            })();
        }
    }

    this.GetImage = function(name) {
        var sprite = sprites[name];
        if (typeof(sprite)=='string') return this.GetImage(sprite);
        return sprite;
    };

    this.IsReady = function(){ return (initializedSprites == totalSprites); };
};

pgf.game.map.MapManager = function(params) {

    var mapData = {};
    var calculatedData = {};
    var dynamicData = { heroes: {} };
    var instance = this;

    function LoadMap(version) {
        jQuery.ajax({   dataType: 'json',
                        type: 'get',
                        url: params.RegionUrl(version),
                        success: function(data, request, status) {
                            mapData = data;

                            calculatedData.mapInfo = CalculateMapInfo(mapData);

                            instance.mapWidth = data.width;
                            instance.mapHeight = data.height;

                            jQuery(document).trigger(pgf.game.map.events.DATA_UPDATED);
                        },
                        error: function() {
                        },
                        complete: function() {
                        }
                    });
    }

    function CalculateMapInfo(mapData) {
        var w = mapData.width;
        var h = mapData.height;

        var mapInfo = [];
        for (var i=0; i<h; ++i) {
            var row = [];
            for (var j=0; j<w; ++j) {
                row.push({});
            }
            mapInfo.push(row);
        }

        for(var road_id in mapData.roads) {
            var road = mapData.roads[road_id];

            if (!road.exists) continue;

            var point_1 = mapData.places[road.point_1_id];
            var pos = point_1.pos;
            var x = point_1.pos.x;
            var y = point_1.pos.y;

            for(var i=0; i<road.path.length; ++i) {

                mapInfo[y][x][road.path[i]] = true;
                mapInfo[y][x].road = true;

                switch(road.path[i]) {
                case 'l': x -= 1; break;
                case 'r': x += 1; break;
                case 'u': y -= 1; break;
                case 'd': y += 1; break;
                }
            }
            mapInfo[y][x].road = true;
        }

        for(var building_id in mapData.buildings) {
            var building = mapData.buildings[building_id];
            mapInfo[building.pos.y][building.pos.x].building = true;
        }

        return mapInfo;
    }

    function GetMapDataForRect(x, y, w, h) {
        return { mapData: mapData,
                 dynamicData: dynamicData,
                 calculatedData: calculatedData};
    }

    function GetPlaceData(placeId) {
        if (mapData.places) return mapData.places[placeId];
        return undefined;
    }

    function GetBuildingData(buildingId) {
        return mapData.buildings[buildingId];
    }

    function GetCellData(x, y) {
        var data = { place: undefined,
                     building: undefined};

        for (var placeId in mapData.places) {
            var place = mapData.places[placeId];

            if (place.pos.x == x && place.pos.y == y) {
                data.place = place;
                break;
            }
        }

        for (var buildingId in mapData.buildings) {
            var building = mapData.buildings[buildingId];

            if (building.pos.x == x && building.pos.y == y) {
                data.building = building;
                break;
            }
        }

        return data;
    }

    jQuery(document).bind(pgf.game.events.DATA_REFRESHED, function(e, game_data) {
        if (game_data.account && game_data.account.hero) {
            dynamicData.hero = game_data.account.hero;
        }

        if (mapData && game_data.map_version != mapData.map_version) {
            LoadMap(game_data.map_version);
        }
    });

    this.mapWidth = 0;
    this.mapHeight = 0;

    this.GetMapDataForRect = GetMapDataForRect;
    this.GetPlaceData = GetPlaceData;
    this.GetCellData = GetCellData;

    LoadMap(params.currentMapVersion);
};

pgf.game.map.Map = function(selector, params) {

    var map = jQuery(selector);
    var canvas = jQuery('.pgf-map-canvas', selector);

    var canvasWidth = undefined;
    var canvasHeight = undefined;params.canvasWidth;

    function SyncCanvasSize() {
        canvasWidth = jQuery('#pgf-map-container').width()-20;
        canvasHeight = params.canvasWidth;

        canvas.get(0).width = canvasWidth;
        canvas.get(0).height = canvasHeight;

        map.css({width: canvasWidth,
                 height: canvasHeight });
    }
    SyncCanvasSize();

    var spritesManager = params.spritesManager;
    var mapManager = widgets.mapManager;

    var pos = {x: 0, y: 0};

    var TILE_SIZE = params.tileSize;

    var selectedTile = undefined;

    var navigationLayer = new pgf.game.map.NavigationLayer(jQuery('.pgf-navigation-layer'),
                                                           { OnDrag: OnMove,
                                                             OnMouseEnter: OnMouseEnter,
                                                             OnMove: OnMouseMove,
                                                             OnMouseLeave: OnMouseLeave,
                                                             OnClick: OnClick,
                                                             w: canvasWidth,
                                                             h: canvasHeight
                                                           });

    var INITIALIZATION_INFO_LOADED = false;
    var INITIALIZATION_SPRITES_LOADED = false;
    var INITIALIZATION_MAP_LOADED = false;

    var activated = false;

    jQuery(window).resize(function(e){
        SyncCanvasSize();
        var data = mapManager.GetMapDataForRect(pos.x, pos.y, canvasWidth, canvasHeight);
        Draw(data);
    });

    function IsInitialized() {
        return INITIALIZATION_INFO_LOADED && INITIALIZATION_SPRITES_LOADED && INITIALIZATION_MAP_LOADED;
    }

    function OnClick(offsetX, offsetY) {
        var x =  Math.floor(-(pos.x - offsetX) / TILE_SIZE);
        var y = Math.floor(-(pos.y - offsetY) / TILE_SIZE);

        var cellData = mapManager.GetCellData(x, y);

        pgf.ui.dialog.Create({ fromUrl: pgf.urls['game:map:cell_info'](x, y),
                               OnOpened: function(dialog) {
                                   pgf.base.InitializeTabs('game-map-cell-info', 'map',
                                                           [[jQuery('.pgf-cell-description-button', dialog), 'description'],
                                                            [jQuery('.pgf-cell-persons-button', dialog), 'persons'],
                                                            [jQuery('.pgf-cell-place-parameters-button', dialog),'place-parameters'],
                                                            [jQuery('.pgf-cell-place-bills-button', dialog),'place-bills'],
                                                            [jQuery('.pgf-cell-place-modifiers-button', dialog), 'place-modifiers'],
                                                            [jQuery('.pgf-cell-place-chronicle-button', dialog), 'place-chronicle'],
                                                            [jQuery('.pgf-cell-building-button', dialog), 'building'],
                                                            [jQuery('.pgf-cell-map-button', dialog), 'map'],
                                                            [jQuery('.pgf-cell-debug-button', dialog), 'debug']]);
                                   jQuery('[rel="tooltip"]', dialog).tooltip(pgf.base.tooltipsArgs);

                                   if (widgets.abilities) {
                                       widgets.abilities.UpdateButtons();
                                       widgets.abilities.RenderAbility(pgf.game.constants.abilities.building_repair);
                                       jQuery('.angel-ability', dialog).toggleClass('pgf-hidden', false);
                                   }

                               },
                               OnClosed: function(dialog) {
                                   pgf.base.HideTooltips(dialog);
                               }
                             });
    }

    function OnMouseEnter() {
    }

    function OnMouseLeave() {
        selectedTile = undefined;
        OnMove(0, 0);
    }

    function OnMouseMove(offsetX, offsetY) {
        var needRedraw = false;
        var x =  Math.floor(-(pos.x - offsetX) / TILE_SIZE);
        var y = Math.floor(-(pos.y - offsetY) / TILE_SIZE);
        if (!selectedTile || selectedTile.x != x || selectedTile.y != y) {
            needRedraw = true;
        }
        selectedTile = { x: x, y: y };

        if (needRedraw) OnMove(0, 0);
    }

    function OnMove(dx, dy) {

        if (!IsInitialized()) return;

        pos.x -= dx;
        pos.y -= dy;

        if (pos.x > 0) pos.x = 0;
        if (pos.y > 0) pos.y = 0;
        if (mapManager.mapWidth * TILE_SIZE + pos.x < canvasWidth) pos.x = canvasWidth - mapManager.mapWidth * TILE_SIZE;
        if (mapManager.mapHeight * TILE_SIZE + pos.y < canvasHeight) pos.y = canvasHeight - mapManager.mapHeight * TILE_SIZE;

        var data = mapManager.GetMapDataForRect(pos.x, pos.y, canvasWidth, canvasHeight);
        Draw(data);
    }

    ///////////////////////////////////////////////////
    // cell highlighting
    ///////////////////////////////////////////////////
    var _highlightingBorder = undefined;
    var _highlightingPositions = {};
    function GetHighlightingBorder() {
        if (!_highlightingBorder) {
            image = spritesManager.GetImage('cell_highlighting');
            _highlightingBorder = jQuery('<div></div>').css({'width': TILE_SIZE+'px',
                                                             'height': TILE_SIZE+'px',
                                                             'background': 'url("'+image.src+'") no-repeat scroll -'+image.x+'px -'+image.y+'px',
                                                             'position': 'relative',
                                                             'display': 'none',
                                                             'z-index': parseInt(canvas.css('z-index')) + 1});
            map.append(_highlightingBorder);
        }
        return _highlightingBorder;
    }

    function UpdateHighlightingPosition(x_, y_) {
        if (x_ != undefined) _highlightingPositions.x = Math.round(x_);
        if (y_ != undefined) _highlightingPositions.y = Math.round(y_);

        var posX = Math.floor(pos.x);
        var posY = Math.floor(pos.y);

        var x = parseInt(posX + _highlightingPositions.x * TILE_SIZE);
        var y = parseInt(posY + _highlightingPositions.y * TILE_SIZE);

        GetHighlightingBorder().css({'left': x+'px', 'top': y+'px'});
    }

    function HighlightCell(x_, y_) {
        UpdateHighlightingPosition(x_, y_);
        GetHighlightingBorder().effect("pulsate", { times:9, mode: "hide"}, 250);
    }
    ///////////////////////////////////////////////////

    function CenterOnHero() {
        var fullData = mapManager.GetMapDataForRect(pos.x, pos.y, canvasWidth, canvasHeight);
        var data = fullData.mapData;

        var hero = fullData.dynamicData.hero;

        if (!hero) return;

        var heroPosition = GetHeroPosition(data, hero);

        var x = heroPosition.x * TILE_SIZE - canvasWidth / 2;
        var y = heroPosition.y * TILE_SIZE - canvasHeight / 2;

        OnMove(x + pos.x, y + pos.y);

        HighlightCell(heroPosition.x, heroPosition.y);

        return;
    }

    function CenterOnPlace(placeId) {
        var fullData = mapManager.GetMapDataForRect(pos.x, pos.y, canvasWidth, canvasHeight);
        var data = fullData.mapData;

        var place = data.places[placeId];

        var x = place.pos.x * TILE_SIZE - canvasWidth / 2;
        var y = place.pos.y * TILE_SIZE - canvasHeight / 2;

        OnMove(x + pos.x, y + pos.y);

        HighlightCell(place.pos.x, place.pos.y);

        return;
    };

    function GetRoadTile(map, y, x) {
        var result = {name: '',
                      rotate: 0};
        var l = 0;
        var r = 0;
        var u = 0;
        var d = 0;

        var cell = map[y][x];
        var l_cell = x > 0 ? map[y][x-1] : {};
        var r_cell = x < map[y].length-1 ? map[y][x+1] : {};
        var u_cell = y > 0 ? map[y-1][x] : {};
        var d_cell = y < map.length-1 ? map[y+1][x] : {};

        if (cell.l || l_cell.r) l = 1;
        if (cell.r || r_cell.l) r = 1;
        if (cell.u || u_cell.d) u = 1;
        if (cell.d || d_cell.u) d = 1;

        var sum = l + r + u + d;

        if (sum==4) return {name: 'r4', scaleX: 1, scaleY: 1};

        if (sum==3) {
            if (!l) return {name: 'r3', rotate: 90, scaleX: 1, scaleY: 1};
            if (!r) return {name: 'r3', rotate: 270, scaleX: 1, scaleY: 1};
            if (!u) return {name: 'r3', rotate: 180, scaleX: 1, scaleY: -1};
            if (!d) return {name: 'r3', rotate: 0, scaleX: 1, scaleY: 1};
        }

        if (l && u) return {name: 'r_angle', rotate: 0, scaleX: 1, scaleY: 1};
        if (l && r) return {name: 'r_horiz', rotate: 0, scaleX: 1, scaleY: 1};
        if (l && d) return {name: 'r_angle', rotate: 270, scaleX: 1, scaleY: 1};

        if (u && r) return {name: 'r_angle', rotate: 90, scaleX: 1, scaleY: 1};
        if (u && d) return {name: 'r_vert', rotate: 0, scaleX: 1, scaleY: 1};

        if (r && d) return {name: 'r_angle', rotate: 180, scaleX: 1, scaleY: 1};

        if (l) return {name: 'r1', rotate: 180, scaleX: 1, scaleY: 1};
        if (r) return {name: 'r1', rotate: 0, scaleX: 1, scaleY: 1};
        if (u) return {name: 'r1', rotate: 270, scaleX: 1, scaleY: 1};
        if (d) return {name: 'r1', rotate: 90, scaleX: 1, scaleY: 1};

        alert('check cell: ('+x+', '+y+')');
        return {name: 'r_line', rotate: 0};
    }

    function GetHeroPosition(data, hero) {

        if (hero.position.place_id != null) {
            var place = data.places[hero.position.place_id];
            return {x: place.pos.x, y: place.pos.y};
        }

        if (hero.position.road_id != null) {
            var road = data.roads[hero.position.road_id];
            var point_1 = data.places[road.point_1_id];
            var point_2 = data.places[road.point_2_id];

            var percents = hero.position.percents;
            var path = road.path;
            var x = point_1.pos.x;
            var y = point_1.pos.y;
            if (hero.position.invert_direction) {
                percents = 1 - percents;
            }
            var length = percents * path.length;
            for (var i=0; i+1<length; ++i) {
                switch(path[i]) {
                case 'l': x -= 1; break;
                case 'r': x += 1; break;
                case 'u': y -= 1; break;
                case 'd': y += 1; break;
                }
            }

            var delta = length - i;
            switch(path[i]) {
            case 'l': x -= delta; break;
            case 'r': x += delta; break;
            case 'u': y -= delta; break;
            case 'd': y += delta; break;
            }

            return {x: x, y: y};
        }

        if (hero.position.coordinates.to.x ||
            hero.position.coordinates.to.y ||
            hero.position.coordinates.from.x ||
            hero.position.coordinates.from.y) {

            var to_x = hero.position.coordinates.to.x;
            var to_y = hero.position.coordinates.to.y;
            var from_x = hero.position.coordinates.from.x;
            var from_y = hero.position.coordinates.from.y;
            var percents = hero.position.percents;

            var x = from_x + (to_x - from_x) * percents;
            var y = from_y + (to_y - from_y) * percents;

            return {x: x, y: y};
        }
    }

    function DrawText(context, text, textWidth, textHeight, x, y) {

        var rectDelta = 2;

        context.textBaseline = 'top';

        context.fillStyle="#000000";
        context.globalAlpha=0.75;
        context.fillRect(x-rectDelta, y, textWidth+rectDelta*2, textHeight+rectDelta*2);
        context.globalAlpha=1;
        context.strokeStyle="#000000";
        context.strokeRect(x-rectDelta, y, textWidth+rectDelta*2, textHeight+rectDelta*2);

        context.fillStyle="#ffffff";
        context.fillText(text, x, y);
    }

    function Draw(fullData) {

        if (!IsInitialized()) return;

        var data = fullData.mapData;
        var dynamicData = fullData.dynamicData;
        var calculatedData = fullData.calculatedData;

        var context = canvas.get(0).getContext("2d");

        context.save();

        var posX = Math.floor(pos.x);
        var posY = Math.floor(pos.y);
        var w = data.width;
        var h = data.height;
        var terrain = data.terrain;

        for (var i=0; i<h; ++i) {
            for (var j=0; j<w; ++j) {
                var image = undefined;
                var rotate = 0;

                var x = posX + j * TILE_SIZE;
                var y = posY + i * TILE_SIZE;

                var imageName = pgf.game.constants.TERRAIN_ID_TO_STR[terrain[i][j]];

                var cellInfo = calculatedData.mapInfo[i][j];

                if (cellInfo.road || cellInfo.building) {
                    image = spritesManager.GetImage('BOARD_'+imageName);
                    image.Draw(context, x, y);
                }
                else {
                    image = spritesManager.GetImage(imageName);
                    image.Draw(context, x, y);
                }

                if (calculatedData.mapInfo[i][j].road) {
                    var roadTile = GetRoadTile(calculatedData.mapInfo, i, j);
                    image = spritesManager.GetImage(roadTile.name);
                    rotate = roadTile.rotate * Math.PI / 180;

                    context.save();
                    var translated_x = x + TILE_SIZE / 2;
                    var translated_y = y + TILE_SIZE / 2;
                    context.translate(translated_x, translated_y);
                    context.rotate(rotate);
                    image.Draw(context, -TILE_SIZE/2, -TILE_SIZE/2);
                    context.restore();
                }

            }
        }

        context.font="10px sans-serif";
        for (var building_id in data.buildings) {
            var building = data.buildings[building_id];
            var spriteName = 'BUILDING_' + pgf.game.constants.BUILDING_TYPE_TO_STR[building.type];
            var image = spritesManager.GetImage(spriteName);
            image.Draw(context,
                       posX + building.pos.x * TILE_SIZE,
                       posY + building.pos.y * TILE_SIZE);
        }

        context.font="12px sans-serif";
        for (var place_id in data.places) {
            var place = data.places[place_id];
            var spriteName = 'city_' + pgf.game.constants.RACE_TO_STR[place.race].toLowerCase();

            if (place.size < 3) { spriteName += '_small'; }
            else { if (place.size < 6) { spriteName += '_medium'; }
                   else { if (place.size < 9) { spriteName += '_large'; }
                          else spriteName += '_capital';
                        }}

            var image = spritesManager.GetImage(spriteName);
            image.Draw(context,
                       posX + place.pos.x * TILE_SIZE,
                       posY + place.pos.y * TILE_SIZE);

            var text = '('+place.size+') '+place.name;
            var textWidth = context.measureText(text).width;

            DrawText(context,
                     text,
                     textWidth,
                     12,
                     Math.round(posX + place.pos.x * TILE_SIZE + TILE_SIZE / 2 - textWidth / 2),
                     Math.round(posY + (place.pos.y + 1) * TILE_SIZE) + 2);
        }

        var hero = dynamicData.hero;

        if (hero) {

            var heroPosition = GetHeroPosition(data, hero);
            // hero.base.race/gender
            var heroImage = 'hero_'+
                pgf.game.constants.RACE_TO_STR[hero.base.race].toLowerCase() +
                '_' + pgf.game.constants.GENDER_TO_STR[hero.base.gender].toLowerCase();

            var reflectNeeded = false;

            if (hero.position.road_id != null) {
                var road = data.roads[hero.position.road_id];
                var point_1 = data.places[road.point_1_id];
                var point_2 = data.places[road.point_2_id];


                if (hero.position.invert_direction) {
                    var tmp = point_1;
                    point_1 = point_2;
                    point_2 = tmp;
                }

                if (point_1.pos.x < point_2.pos.x) {
                    reflectNeeded = true;
                }
            }

            if (hero.position.coordinates.to.x ||
                hero.position.coordinates.to.y ||
                hero.position.coordinates.from.x ||
                hero.position.coordinates.from.y) {

                var to_x = hero.position.coordinates.to.x;
                var from_x = hero.position.coordinates.from.x;

                if (from_x < to_x) {
                    reflectNeeded = true;
                }
            }

            var image = spritesManager.GetImage(heroImage);

            var heroX = parseInt(posX + heroPosition.x * TILE_SIZE, 10);
            var heroY = parseInt(posY + heroPosition.y * TILE_SIZE, 10) - 12;

            if (reflectNeeded) {
                context.save();
                context.scale(-1, 1);
                heroX *= -1;
                heroX -= TILE_SIZE;
            }

            image.Draw(context, heroX, heroY);

            if (reflectNeeded) {
                context.restore();
            }
        }

        if (selectedTile) {

            var x = posX + selectedTile.x * TILE_SIZE;
            var y = posY + selectedTile.y * TILE_SIZE;

            if (0 <= x && x < w * TILE_SIZE &&
                0 <= y && y < h * TILE_SIZE) {
                var image = spritesManager.GetImage('select_land');
                image.Draw(context, x, y);
            }
        }

        context.restore();

        UpdateHighlightingPosition();
    }

    function Activate() {
        activated = true;
        OnMove(0, 0);
        CenterOnHero();
    }

    function Refresh(game_data) {
        OnMove(0, 0);
    }

    jQuery(document).bind(pgf.game.events.DATA_REFRESHED,
                          function(e, game_data) {
                              INITIALIZATION_INFO_LOADED = true;

                              if (IsInitialized() && !activated) Activate();

                              widgets.map.Refresh(game_data);
                          });

    jQuery(document).bind(pgf.game.resources.events.SPRITES_LOADED,
                          function() {
                              INITIALIZATION_SPRITES_LOADED = true;
                              if (IsInitialized() && !activated) Activate();
                          });

    jQuery(document).bind(pgf.game.map.events.DATA_UPDATED,
                          function() {
                              INITIALIZATION_MAP_LOADED = true;
                              if (IsInitialized() && !activated) Activate();

                              widgets.map.Refresh();
                          });


    this.Draw = Draw;
    this.CenterOnHero = CenterOnHero;
    this.CenterOnPlace = CenterOnPlace;
    this.Refresh = Refresh;
};

pgf.game.map.NavigationLayer = function(selector, params) {

    var container = jQuery(selector);
    container.css({width: params.w,
                   height: params.h});

    var pos = {x: 0, y: 0};

    var OnDrag = params.OnDrag;
    var OnMove = params.OnMove;
    var OnMouseEnter = params.OnMouseEnter;
    var OnMouseLeave = params.OnMouseLeave;
    var OnClick = params.OnClick;

    var layer = this;

    var isDragging = false;

    function OnStartDragging(left, top) {
        pos = {x: left, y: top};
        isDragging = false;
    };

    function OnLayerDrag(left, top) {
        isDragging = true;

        var newPos = {x: left,
                      y: top};

        var delta = {x: pos.x - newPos.x,
                     y: pos.y - newPos.y};

        pos = newPos;

        OnDrag(delta.x, delta.y);
    };

    function OnStopDragging() {
        pos = { x: 0, y: 0};
        isDragging = false;
    };

    container.draggable({start: function(e, ui){OnStartDragging(ui.position.left, ui.position.top);},
                         drag: function(e, ui){OnLayerDrag(ui.position.left, ui.position.top);},
                         stop: function(e, ui){OnStopDragging();},
                         cursor: 'crosshair',
                         helper: 'original',
                         revert: true,
                         revertDuration: 0,
                         scroll: false
                        });

    function _OnMouseMove(pageX, pageY) {
        var offset = container.offset();
        var x = pageX - offset.left;
        var y = pageY - offset.top;
        OnMove(pos.x + x, pos.y + y);
    }

    function _OnClick(pageX, pageY) {
        var offset = container.offset();
        var x = pageX - offset.left;
        var y = pageY - offset.top;
        OnClick(x, y);
    }

    container.mousemove(function(e) {_OnMouseMove(e.pageX, e.pageY);});
    container.mouseenter(function(e){OnMouseEnter();});
    container.mouseleave(function(e){OnMouseLeave();});
    container.click(function(e){_OnClick(e.pageX, e.pageY);});

    container.bind('touchstart', function(e){
                       e.preventDefault(); //prevent block selection on logn touch
                       var touch = e.originalEvent.touches[0] || e.originalEvent.changedTouches[0];
                       OnStartDragging(touch.pageX, touch.pageY);
                   });
    container.bind('touchmove', function(e) {
                       e.preventDefault();
                       var touch = e.originalEvent.touches[0] || e.originalEvent.changedTouches[0];
                       OnLayerDrag(touch.pageX, touch.pageY);
                   });
    container.bind('touchend', function(e){
                       e.preventDefault(); //prevent block selection on logn touch

                       var touch = e.originalEvent.touches[0] || e.originalEvent.changedTouches[0];

                       if (!isDragging) {
                           // emulate mouse click, since we prevent default events handlers
                           _OnClick(touch.pageX, touch.pageY);
                       }

                       OnStopDragging();
                   });
};
