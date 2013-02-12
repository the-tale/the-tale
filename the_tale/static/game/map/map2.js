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

pgf.game.resources.Image = function(canvas) {
    var image = canvas;

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

                var tmpCanvas = document.createElement('canvas');
                tmpCanvas.width = data.w;
                tmpCanvas.height = data.h;
                var tmpContext = tmpCanvas.getContext('2d');

                tmpContext.drawImage(properties.image,
                                     data.x, data.y, data.w, data.h,
                                     0, 0, data.w, data.h);

                sprites[spriteName] = new pgf.game.resources.Image(tmpCanvas);
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
    var updater = params.updater;
    var instance = this;

    jQuery.ajax({
        dataType: 'json',
        type: 'get',
        url: params.regionUrl,
        success: function(data, request, status) {
            mapData = data;

            calculatedData.roadsMap = CalculateRoads(mapData);

            instance.mapWidth = data.width;
            instance.mapHeight = data.height;

            jQuery(document).trigger(pgf.game.map.events.DATA_UPDATED);
        },
        error: function() {
        },
        complete: function() {
        }
    });

    function CalculateRoads(mapData) {
        var w = mapData.width;
        var h = mapData.height;

        var roadsMap = [];
        for (var i=0; i<h; ++i) {
            var row = [];
            for (var j=0; j<w; ++j) {
                row.push({});
            }
            roadsMap.push(row);
        }

        for(var road_id in mapData.roads) {
            var road = mapData.roads[road_id];

            if (!road.exists) continue;

            var point_1 = mapData.places[road.point_1_id];
            var x = point_1.x;
            var y = point_1.y;

            for(var i=0; i<road.path.length; ++i) {

                roadsMap[y][x][road.path[i]] = true;
                roadsMap[y][x].road = true;

                switch(road.path[i]) {
                case 'l': x -= 1; break;
                case 'r': x += 1; break;
                case 'u': y -= 1; break;
                case 'd': y += 1; break;
                }
            }
            roadsMap[y][x].road = true;
        }

        return roadsMap;
    }

    function RefreshHero(hero) {
        if (hero) {
            dynamicData.heroes[hero.id] = hero;
        }
    }

    function GetMapDataForRect(x, y, w, h) {
        return { mapData: mapData,
                 dynamicData: dynamicData,
                 calculatedData: calculatedData};
    }

    function GetPlaceData(placeId) {
        return mapData.places[placeId];
    }

    function GetCellData(x, y) {
        var data = { place: undefined };

        for (var placeId in mapData.places) {
            var place = mapData.places[placeId];

            if (place.x == x && place.y == y) {
                data.place = place;
                break;
            }
        }

        return data;
    }

    jQuery(document).bind(pgf.game.events.DATA_REFRESHED, function(e, game_data){

        RefreshHero(game_data.hero);

        if (params.OnDataUpdated) {
            params.OnDataUpdated();
        }

    });

    this.mapWidth = 0;
    this.mapHeight = 0;

    this.GetMapDataForRect = GetMapDataForRect;
    this.GetPlaceData = GetPlaceData;
    this.GetCellData = GetCellData;
};

pgf.game.map.Map = function(selector, params) {

    var map = jQuery(selector);
    var canvas = jQuery('.pgf-map-canvas', selector);

    // var canvasWidth = canvas.width();
    // var canvasHeight = canvas.height();

    // TODO: do something with this
    var canvasWidth = jQuery('#pgf-map-container').width()-20;
    var canvasHeight = 400; //jQuery('#pgf-map-container').height();

    canvas.get(0).width = canvasWidth;
    canvas.get(0).height = canvasHeight;

    // var canvasWidth = canvas.context.width;
    // var canvasHeight = canvas.context.height;

    map.css({width: canvasWidth,
             height: canvasHeight });

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
                                                            [jQuery('.pgf-cell-place-modifiers-button', dialog), 'place-modifiers'], 
                                                            [jQuery('.pgf-cell-map-button', dialog), 'map'], 
                                                            [jQuery('.pgf-cell-debug-button', dialog), 'debug']]);
                                   jQuery('[rel="tooltip"]', dialog).tooltip(pgf.base.tooltipsArgs);
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

    function CenterOnHero() {
        var fullData = mapManager.GetMapDataForRect(pos.x, pos.y, canvasWidth, canvasHeight);
        var data = fullData.mapData;
        var dynamicData = fullData.dynamicData;

        for (var hero_id in dynamicData.heroes) {
            var hero = dynamicData.heroes[hero_id];

            var heroPosition = GetHeroPosition(data, hero);

            var x = heroPosition.x * TILE_SIZE - canvasWidth / 2;
            var y = heroPosition.y * TILE_SIZE - canvasHeight / 2;

            OnMove(x + pos.x, y + pos.y);

            return;
        }
    }

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

        if (hero.position.place) {
            var place = data.places[hero.position.place.id];
            return {x: place.x, y: place.y};
        }

        if (hero.position.road) {
            var road = data.roads[hero.position.road.id];
            var point_1 = data.places[road.point_1_id];
            var point_2 = data.places[road.point_2_id];

            var percents = hero.position.percents;
            var path = road.path;
            var x = point_1.x;
            var y = point_1.y;
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

                if (calculatedData.roadsMap[i][j].road) {

                    image = spritesManager.GetImage('ROAD_'+imageName);
                    image.Draw(context, x, y);

                    var roadTile = GetRoadTile(calculatedData.roadsMap, i, j);
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
                else {
                    image = spritesManager.GetImage(imageName);
                    image.Draw(context, x, y);
                }
            }
        }

        context.fillStyle    = '#000';
        context.font         = 'bold 14px sans-serif';
        context.textBaseline = 'top';
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
                       posX + place.x * TILE_SIZE,
                       posY + place.y * TILE_SIZE);

            var text = '('+place.size+') '+place.name;

            context.font="12px sans-serif";
            var textSize = context.measureText(text);

            var textX = Math.round(posX + place.x * TILE_SIZE + TILE_SIZE / 2 - textSize.width / 2);
            var textY = Math.round(posY + (place.y + 1) * TILE_SIZE) + 2;

            var rectDelta = 2;
            var textHeight = 12;

            context.fillStyle="#000000";
            context.globalAlpha=0.75;
            context.fillRect(textX-rectDelta, textY, textSize.width+rectDelta*2, textHeight+rectDelta*2);
            context.globalAlpha=1;
            context.strokeStyle="#000000";
            context.strokeRect(textX-rectDelta, textY, textSize.width+rectDelta*2, textHeight+rectDelta*2);

            context.fillStyle="#ffffff";
            context.fillText(text, textX, textY);
        }

        for (var hero_id in dynamicData.heroes) {
            var hero = dynamicData.heroes[hero_id];

            var heroPosition = GetHeroPosition(data, hero);
            // hero.base.race/gender
            var heroImage = 'hero_'+ 
                pgf.game.constants.RACE_TO_STR[hero.base.race].toLowerCase() +
                '_' + pgf.game.constants.GENDER_TO_STR[hero.base.gender].toLowerCase();

            var reflectNeeded = false;

            if (hero.position.road) {
                var road = data.roads[hero.position.road.id];
                var point_1 = data.places[road.point_1_id];
                var point_2 = data.places[road.point_2_id];


                if (hero.position.invert_direction) {
                    var tmp = point_1;
                    point_1 = point_2;
                    point_2 = tmp;
                }

                if (point_1.x > point_2.x) {
                    reflectNeeded = true;
                    // heroImage = 'hero_left';
                }
            }

            if (hero.position.coordinates.to.x ||
                hero.position.coordinates.to.y ||
                hero.position.coordinates.from.x ||
                hero.position.coordinates.from.y) {

                var to_x = hero.position.coordinates.to.x;
                var from_x = hero.position.coordinates.from.x;

                if (from_x > to_x) {
                    reflectNeeded = true;
                    // heroImage = 'hero_left';
                }
            }

            var image = spritesManager.GetImage(heroImage);

            var heroX = parseInt(posX + heroPosition.x * TILE_SIZE, 10);
            var heroY = parseInt(posY + heroPosition.y * TILE_SIZE, 10) - 12;

            if (reflectNeeded) {
                context.save(); 
                context.scale(-1, 1);
                heroX *= -1;
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
    this.Refresh = Refresh;
};

pgf.game.map.NavigationLayer = function(selector, params) {

    var container = jQuery(selector);
    container.css({width: params.w,
                   height: params.h });

    var pos = {x: 0, y: 0};

    var OnDrag = params.OnDrag;
    var OnMove = params.OnMove;
    var OnMouseEnter = params.OnMouseEnter;
    var OnMouseLeave = params.OnMouseLeave;
    var OnClick = params.OnClick;

    var layer = this;

    function OnStartDragging(e, ui) {
        pos = {x: ui.position.left,
               y: ui.position.top};
    };

    function OnLayerDrag(e, ui) {
        var newPos = {x: ui.position.left,
                      y: ui.position.top};

        var delta = {x: pos.x - newPos.x,
                     y: pos.y - newPos.y};

        pos = newPos;

        OnDrag(delta.x, delta.y);
    };

    function OnStopDragging(e, ui) {
        pos = { x: 0, y: 0};
    };

    container.draggable({start: function(e, ui){OnStartDragging(e, ui);},
                         drag: function(e, ui){OnLayerDrag(e, ui);},
                         stop: function(e, ui){OnStopDragging(e, ui);},
                         cursor: 'crosshair',
                         helper: 'original',
                         revert: true,
                         revertDuration: 0,
                         scroll: false
                        });

    container.mousemove(function(e) {
                            var offset = container.offset();
                            var x = e.pageX - offset.left;
                            var y = e.pageY - offset.top;
                            OnMove(pos.x + x, pos.y + y);
                        });
    container.mouseenter(function(e){OnMouseEnter();});
    container.mouseleave(function(e){OnMouseLeave();});
    container.click(function(e){
                        var offset = container.offset();
                        var x = e.pageX - offset.left;
                        var y = e.pageY - offset.top;
                        OnClick(pos.x + x, pos.y + y);
                    });
};
