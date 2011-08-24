
if (!window.pgf) {
    pgf = {};
}

if (!pgf.tooltips) {
    pgf.tooltips = {};
}

pgf.tooltips.Init = function() {

    function GetTooltipData() {
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

    jQuery.fn.tipsy.defaults = {
        delayIn: 0,      // delay before showing tooltip (ms)
        delayOut: 0,     // delay before hiding tooltip (ms)
        fade: false,     // fade tooltips in/out?
        fallback: '',    // fallback text to use when no tooltip text
        gravity: jQuery.fn.tipsy.autoWE,    // gravity
        html: true,     // is tooltip content HTML?
        live: true,     // use live event support?
        offset: 0,       // pixel offset of tooltip from element
        opacity: 0.8,    // opacity of tooltip
        title: GetTooltipData,  // attribute/callback containing tooltip text
        trigger: 'hover' // how tooltip is triggered - hover | focus | manual
    };

    jQuery('[data-tooltip]').tipsy();

};


