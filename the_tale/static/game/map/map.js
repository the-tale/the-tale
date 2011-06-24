
if (!window.pgf) {
    pgf = {};
}

if (!pgf.game) {
    pgf.game = {};
}

if (!pgf.game.map) {
    pgf.game.map = {};
}

pgf.game.map.Map = function(params) {

    var zIndexBegin = params.zIndexBegin;
    var root = jQuery(params.root); // selector
    var layers = params.layers;     // []
    var zooms = params.zooms;       // [1]
    var wndZoom = params.curZoom;   // 0
    var wndZoomValue = zooms[wndZoom];
    var wndPos = params.wndPos;     // {x, y}
    var wndSize = {w: root.width(), 
                   h: root.height()};// {w, h}
    var mapPos = params.mapPos;
    var mapSize = params.mapSize;   // {w, h}

    var container = undefined;
    var board = undefined;

    var OnChangeCallback = params.OnChange || function(){};

    var map = this;

    this.GetPos = function() {
        return {x: wndPos.x,
                y: wndPos.y};
    };

    this.GetZoom = function() {
        return { lvl: wndZoom,
                 value: wndZoomValue};
    };

    this.Init = function() {
        container = jQuery("<div class='pgf-map-container'></div>").appendTo(root);
        board = jQuery("<div class='pgf-map-board'></div>").appendTo(container);

        for (var i in layers) {
            var layer = jQuery("<div class='pgf-map-layer'></div>").appendTo(board);
            layer.css({'z-index': zIndexBegin+parseInt(i)});
            layers[i].Init({container: layer,
                            map: map});
        }
        OnChangeCallback(map);
    };

    this.GetBoardSize = function() {
        return {w: board.width(),
                h: board.height()};
    };

    this.ZoomOn = function(zoomLvl) {
        if (zoomLvl < 0) zoomLvl = 0;
        if (zoomLvl >= zooms.length) zoomLvl = zooms.length - 1;

        if (zoomLvl === wndZoom) return;

        for (var i in layers) {
            layers[i].ZoomOn(zoomLvl, zooms[zoomLvl]);
        }

        wndZoom = zoomLvl;
        wndZoomValue = zooms[wndZoom];

        OnChangeCallback(map);
    };
    this.Zoom = function(zoomDelta) {map.ZoomOn(wndZoom + zoomDelta);};
    this.ZoomIn = function(zoomDelta) {map.ZoomOn(wndZoom + 1);};
    this.ZoomOut = function(zoomDelta) {map.ZoomOn(wndZoom + -1);};

    this.MoveOn = function(pos) {
        if (pos.x / wndZoomValue < mapPos.x) pos.x = mapPos.x * wndZoomValue;
        if (pos.y / wndZoomValue < mapPos.y) pos.y = mapPos.y * wndZoomValue;

        if ( (pos.x + wndSize.w) / wndZoomValue > mapPos.x + mapSize.w) pos.x = (mapPos.x + mapSize.w) * wndZoomValue - wndSize.w;
        if ( (pos.y + wndSize.h) / wndZoomValue > mapPos.y + mapSize.h) pos.y = (mapPos.y + mapSize.h) * wndZoomValue - wndSize.h;

        for (var i in layers) {
            layers[i].MoveOn(pos, {x: pos.x - wndPos.x, y: pos.y - wndPos.y} );
        }

        wndPos = pos;

        OnChangeCallback(map);
    };

    this.Move = function(dx, dy) {
        map.MoveOn({ x: wndPos.x+dx,
                     y: wndPos.y+dy});
    };

    this.Init();
};

pgf.game.map.BackgroundLayer = function(params) {

    var pos = {x: 0, y: 0};
    var tileSrc = params.tileSrc;
    var tileSize = params.tileSize;

    var container = undefined;
    var map = undefined;
    var boardSize = undefined;
    var size = {w: 0, h: 0};

    var layer = this;

    this.Create = function() {
        size.w = parseInt(Math.ceil(boardSize.w / tileSize)) + 1;
        size.h = parseInt(Math.ceil(boardSize.h / tileSize)) + 1;

        var html = '<img src="'+tileSrc+'"class="pgf-bg-tile"/>';

        for (var y=0; y<size.h; ++y) {
            for (var x=0; x<size.w; ++x) {
                var img = jQuery(html);
                img.css({widht: tileSize,
                         height: tileSize,
                         left: x*tileSize,
                         top: y*tileSize });
                container.append(img);
            }
        }
    };
    
    this.Init = function(initParams) {
        container = initParams.container;
        map = initParams.map;
        boardSize = map.GetBoardSize();
        layer.Create();
    };
    
    this.ZoomOn = function(zoomLvl, zoomValue) {};

    this.MoveOn = function(newPos, delta) {
        var pos = {left: 0, top: 0};
        if (newPos.x > 0) pos.left = -(newPos.x % tileSize);
        else pos.left = -newPos.x % tileSize - tileSize;
        if (newPos.y > 0) pos.top = -(newPos.y % tileSize);
        else pos.top = -newPos.y % tileSize - tileSize;

        container.css(pos);
    };
};

pgf.game.map.ObjectsLayer = function(params) {

    var container = undefined;
    var map = undefined;
    var boardSize = undefined;

    var pos = {x: 0, y: 0};

    var layer = this;

    var objects = {};

    var zoom = undefined;

    var idPrefix = params.idPrefix;

    this.Init = function(initParams) {
        container = initParams.container;
        map = initParams.map;
        boardSize = map.GetBoardSize();
        zoom = map.GetZoom().value;

        container.css({width: boardSize.w * zoom,
                       height: boardSize.h * zoom});
    };

    this.FormObjectId = function(id) {
        return idPrefix+'-'+id;
    };


    this.UpdateObject = function(data) {
        id = this.FormObjectId(data.id);

        if (id in objects) {
            objects[id].domEl.remove();
        }

        var objectData =  {centerX: data.centerX,
                           centerY: data.centerY,
                           deltaX: data.deltaX,
                           deltaY: data.deltaY};
        data.domElement.attr('id', id).addClass('pgf-map-object');

        container.append(data.domElement);

        objectData.domEl = jQuery('#'+id, container);
        objects[id] = objectData;

        this.UpdateObjectPosition(objectData);
    };

    this.RemoveObject = function(id) {
        if ( !(id in objects)) {
            alert('can not found object with id "'+id+'" in objects layer');
            return;
        }

        id = this.FormObjectId(id);
        objects[id].domElement.remove();

        delete objects[id];
    };

    this.UpdateObjectPosition = function(objectData) {
        objectData.domEl.css({left: objectData.centerX * zoom + objectData.deltaX,
                              top: objectData.centerY * zoom + objectData.deltaY});
    };

    this.ZoomOn = function(zoomLvl, zoomValue) {
        zoom = zoomValue;

        for (objectId in objects) {
            this.UpdateObjectPosition(objects[objectId]);
        }
    };

    this.MoveOn = function(newPos, delta) {
        pos.x = pos.x - delta.x;
        pos.y = pos.y - delta.y;

        container.css({left: pos.x,
                       top: pos.y});
    };

};

pgf.game.map.NavigationLayer = function(params) {

    var container = undefined;
    var map = undefined;
    var boardSize = undefined;

    var pos = {x: 0, y: 0};

    var layer = this;

    this.OnStartDragging = function(e, ui) {
        pos = {x: ui.position.left,
               y: ui.position.top};
    };

    this.OnDrag = function(e, ui) {
        var newPos = {x: ui.position.left,
                      y: ui.position.top};

        var delta = {x: pos.x - newPos.x,
                     y: pos.y - newPos.y};

        pos = newPos;

        map.Move(delta.x, delta.y);
    };

    this.OnStopDragging = function(e, ui) {
    };

    this.Init = function(initParams) {
        container = initParams.container;
        map = initParams.map;
        boardSize = map.GetBoardSize();

        container.draggable({start: function(e, ui){layer.OnStartDragging(e, ui);},
                             drag: function(e, ui){layer.OnDrag(e, ui);},
                             stop: function(e, ui){layer.OnStopDragging(e, ui);},
                             cursor: 'crosshair',
                             helper: 'original',
                             revert: true,
                             revertDuration: 0,
                             scroll: false,
                            });
    };
    
    this.ZoomOn = function(zoomLvl, zoomValue) {};

    this.MoveOn = function(newPos, delta) {};
};

