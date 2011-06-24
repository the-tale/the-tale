
if (!window.pgf) {
    pgf = {};
}

if (!pgf.tooltip) {
    pgf.tooltip = {};
}

pgf.tooltip.TOOLTIP_ID = 'pgf-tooltip-window';
pgf.tooltip.DELAY_BEFORE_SHOW = 500;
pgf.tooltip.tooltipTimer = undefined;
pgf.tooltip.target = undefined;

pgf.tooltip.Set = function(target, type, value) {
    var target = jQuery(target);

    switch(type){
    case 'content': target.data('tooltip-content', value); break;
    case 'text': target.data('tooltip-text', value); break;
    case 'selector': target.data('tooltip-selector', value); break;
    case 'function': target.data('tooltip-function', value); break;
    };
};

pgf.tooltip.GetBody = function(target) {
    var target = jQuery(target);

    var body = '';

    if (target.data('tooltip-content')) {
        body = jQuery(target.data('tooltip-content'));
    }
    if (target.data('tooltip-text')) {
        body = jQuery('<div>'+target.data('tooltip-text')+'</div>');
    }
    if (target.data('tooltip-selector')) {
        body = jQuery(target.data('tooltip-selector')).clone();
    }
    if (target.data('tooltip-function')) {
        body = target.data('tooltip-function')(target);
    }
    body.attr('id', pgf.tooltip.TOOLTIP_ID);

    return body;
};

pgf.tooltip.GetPosition = function(target, body, mousePosition) {

    target = jQuery(target);
    body = jQuery(body);

    var POINTER_DISTANCE = 10;

    var windowSize = { w: jQuery(window).width(),
                       h: jQuery(window).height() };

    var tooltipSize = { w: body.width(),
                        h: body.height() };

    var targetPosition = target.offset();
    targetPosition = { x: targetPosition.left,
                       y: targetPosition.top };
    var targetSize = { w: target.width(),
                       h: target.height() };

    var tooltipPosition = { x: 0, y: 0};

    if (mousePosition.y - tooltipSize.h - POINTER_DISTANCE > 0) {
        tooltipPosition.y = mousePosition.y - tooltipSize.h - POINTER_DISTANCE;
    }
    else {
        tooltipPosition.y = mousePosition.y + POINTER_DISTANCE;
    }

    if (mousePosition.x + tooltipSize.w + POINTER_DISTANCE < windowSize.w ) {
        tooltipPosition.x = mousePosition.x + POINTER_DISTANCE;
    }
    else {
        tooltipPosition.x = mousePosition.x - tooltipSize.w - POINTER_DISTANCE;
    }

    return tooltipPosition;
};

pgf.tooltip.Create = function(target, mousePosition) {

    console.log('show');

    pgf.tooltip.target = target;

    var tooltip = pgf.tooltip.GetBody(target);

    jQuery('body').append(tooltip);

    var position = pgf.tooltip.GetPosition(target, tooltip, mousePosition);

    tooltip.css({left: position.x,
                 top: position.y });

    tooltip.toggleClass('js-hidden', true);

    target.mousemove(function(e){
        var position = pgf.tooltip.GetPosition(target, 
                                               tooltip, 
                                               { x: e.pageX, y: e.pageY } );
        tooltip.css({left: position.x, top: position.y });
    });

    target.one('mouseleave', function(e){
        pgf.tooltip.Hide();
    });

    return tooltip;
};

pgf.tooltip.Hide = function() {

    if (pgf.tooltip.target) {
        pgf.tooltip.target.unbind('mousemove');
        pgf.tooltip.target = undefined;
    }

    if (pgf.tooltip.tooltipTimer) {
        clearTimeout(pgf.tooltip.tooltipTimer);
    }
    jQuery('#'+pgf.tooltip.TOOLTIP_ID).remove();
};

jQuery('.pgf-tooltip-target').live('mouseenter', function(e) {
    var target = jQuery(this);
    var mousePosition = { x: e.pageX, 
                          y: e.pageY };
    
    var tooltip = pgf.tooltip.Create(target, mousePosition);

    pgf.tooltip.tooltipTimer = setTimeout(function(){
        tooltip.toggleClass('js-hidden', false);
    }, pgf.tooltip.DELAY_BEFORE_SHOW);
});

