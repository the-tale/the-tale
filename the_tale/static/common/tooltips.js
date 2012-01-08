
if (!window.pgf) {
    pgf = {};
}

if (!pgf.tooltips) {
    pgf.tooltips = {};
}

pgf.tooltips.GetTooltipData = function() {
    var el = jQuery(this);

    var data = el.data('tooltip');

    if (data.length == 0) {
        alert('tooltip does not set for this element');
        return '';
    }

    if (data[0] == '#') {
        var content = jQuery(data).html();
        if (content.length == 0) {
            alert('can not find html content for this tooltip');
            return '';
        }   
        return content;
    }

    if (data[0] == '.') {
        var content = el.siblings(data).first().html();
        if (content.length == 0) {
            alert('can not find html content for this tooltip');
            return '';
        }   
        return content;
    }

    if (data[0] == '>') {
        var content = el.children('.'+data.substr(1)).first().html();
        if (content.length == 0) {
            alert('can not find html content for this tooltip');
            return '';
        }   
        return content;
    }

    return data;
}

pgf.tooltips.Refresh = function(selector) {
    pgf.tooltips.GetSelector(selector).tipsy();
};

pgf.tooltips.Hide = function(selector) {
    pgf.tooltips.GetSelector(selector).each(function(i, v) {
        jQuery(v).tipsy('hide');
    });
};

pgf.tooltips.GetSelector = function(selector) {
    // var neighbours = jQuery(selector).filter('[data-tooltip]').not('.pgf-template').not('.pgf-empty-template');
    // var children = jQuery('[data-tooltip]', selector).not('.pgf-template').not('.pgf-empty-template');
    // return neighbours.add(children);
    return jQuery('[data-tooltip]', selector);
};

pgf.tooltips.Init = function() {

    jQuery.fn.tipsy.defaults = {
        delayIn: 0,      // delay before showing tooltip (ms)
        delayOut: 0,     // delay before hiding tooltip (ms)
        fade: false,     // fade tooltips in/out?
        fallback: '',    // fallback text to use when no tooltip text
        gravity: jQuery.fn.tipsy.autoWE,    // gravity
        html: true,     // is tooltip content HTML?
        live: false,     // use live event support? - DO NOT USE since problem with tooltip freezing for removed elements
        offset: 0,       // pixel offset of tooltip from element
        opacity: 1,    // opacity of tooltip
        title: pgf.tooltips.GetTooltipData,  // attribute/callback containing tooltip text
        trigger: 'hover' // how tooltip is triggered - hover | focus | manual
    };

    pgf.tooltips.Refresh();
};


