
if (!window.pgf) {
    pgf = {};
}

if (!pgf.base) {
    pgf.base = {};
}

if (typeof(Storage)!=="undefined") {
    pgf.base.settings = {
        _prefix: undefined,
        init: function(prefix) {
            this._prefix = prefix;
        },
        set: function(key, value) {
            localStorage[this._prefix+'_'+key] = value;
        },
        get: function(key, def) {
            key = this._prefix+'_'+key;
            if (!(key in localStorage)) return def;
            return localStorage[key];
        }
    };
}
else {
    pgf.base.settings = {
        init: function(prefix) {},
        set: function(key, value) {},
        get: function(key, def) {return def;}
    };    
}

pgf.base.InitializeTabs = function(settingName, def, tabs) {

    for (var i in tabs) {
        var selector = jQuery(tabs[i][0]);
        var id = tabs[i][1];

        if (pgf.base.settings.get(settingName, def) == id) {
            selector.tab('show');
        }
        
        (function(id) {
            selector.click(function(e){
                               pgf.base.settings.set(settingName, id);
                           });            
        })(id);

    }
};

pgf.base.TooltipPlacement = function (tip, element) {
    var offset = $(element).offset();
    height = $(document).outerHeight();
    width = $(document).outerWidth();
    vert = 0.5 * height - offset.top;
    vertPlacement = vert > 0 ? 'bottom' : 'top';
    horiz = 0.5 * width - offset.left;
    horizPlacement = horiz > 0 ? 'right' : 'left';
    placement = horizPlacement; //Math.abs(horiz) > Math.abs(vert) ?  horizPlacement : vertPlacement;
    return placement;
};

pgf.base.tooltipsArgs = { animation: true,
                          placement: pgf.base.TooltipPlacement,
                          delay: { show: 500,
                                   hide: 100 } };

pgf.base.popoverArgs = { animation: true,
                         placement: pgf.base.TooltipPlacement,
                         delay: { show: 500,
                                  hide: 100 } };

pgf.base.HideTooltips = function(clearedContainer) {
    jQuery('.popover').remove();
    jQuery('.tooltip').remove();

    if (clearedContainer) {
        jQuery('.pgf-has-popover', clearedContainer).each(function(i, el){
                                                              el = jQuery(el);
                                                              el.data('popover').enabled = false;
                                                          });        
    }
};

pgf.base.RenderTemplateList = function(selector, data, newElementCallback, params) {
    
    var container = jQuery(selector);
    var template = jQuery('.pgf-template', container).eq(0);
    var emptyTemplate = jQuery('.pgf-empty-template', container).eq(0);

    container.children().not('.pgf-template').not('.pgf-empty-template').remove();

    for (var i in data) {
        var elementData = data[i];

        var newElement = template
            .clone(false, false)
            .appendTo(container)
            .removeClass('pgf-template');

        newElement.addClass(i % 2 ? 'even' : 'odd');

        if (newElementCallback) {
            newElementCallback(i, elementData, newElement);
        }
    }
};

pgf.base.AutoFormatTime = function() {
    jQuery('.pgf-format-datetime').each(function(i, v){
        var el = jQuery(v);
        var timestamp = parseInt(el.data('timestamp'), 10) * 1000;
        var text = Globalize.format( new Date(timestamp), "d" ) + ' ' + Globalize.format( new Date(timestamp), "t" ) + ' UTC';
        el.text(text);
    });

    jQuery('.pgf-format-date').each(function(i, v){
        var el = jQuery(v);
        var timestamp = parseInt(el.data('timestamp'), 10) * 1000;
        var text = Globalize.format( new Date(timestamp), "d" ) + ' UTC';
        el.text(text);
    });

    jQuery('.pgf-format-time').each(function(i, v){
        var el = jQuery(v);
        var timestamp = parseInt(el.data('timestamp'), 10) * 1000;
        var text = Globalize.format( new Date(timestamp), "t" ) + ' UTC';
        el.text(text);
    });
};

pgf.base.AddPreview = function(blockSelector, contentSourceSelector, previewUrl) {

    var block = jQuery(blockSelector);
    var source = jQuery(contentSourceSelector, block);

    var previewButton = jQuery('.pgf-preview-button', block);
    var editButton = jQuery('.pgf-edit-button', block);
    var editContent = jQuery('.pgf-edit-content', block);
    var previewContent = jQuery('.pgf-preview-content', block);

    function SwitchView(preview) {
        previewButton.toggleClass('pgf-hidden', preview);
        editContent.toggleClass('pgf-hidden', preview);
        editButton.toggleClass('pgf-hidden', !preview);
        previewContent.toggleClass('pgf-hidden', !preview);
    }

    previewButton.click(function(e){
        jQuery.ajax({type: 'post',
                     data: { text: source.val() },
                     url: previewUrl,
                     success: function(data) {
                         previewContent.html(data);
                         SwitchView(true);
                     }
                    });
    });

    editButton.click(function(e){
        SwitchView(false);
    });
};

pgf.base.UpdateStatsBar = function(selector) {
    
    var widget = jQuery(selector);
    var width = widget.width();

    var base = arguments[1];

    for (var i=1; i<arguments.length; ++i)
    {
        var bar = jQuery('.pgf-layer-'+(i-1), widget);
        bar.width( Math.ceil( Math.min(arguments[i], base) / (base + 0.0) * width) );
    }
};

pgf.base.InitBBFields = function(containerSelector) {
    var container = jQuery(containerSelector);
    jQuery('.pgf-bb-command', container).click(function(e){
        e.preventDefault();

        var target = jQuery(e.currentTarget);

        var content = jQuery('textarea', target.parents('.pgf-widget'));

        var text = content.val();

        var textarea = content.get(0);
        
        var selectionStart = textarea.selectionStart;
        var selectionEnd = textarea.selectionEnd;

        var tagName = target.data('tag');
        
        text = text.substring(0, selectionStart) + 
            '[' + tagName + ']' + text.substring(selectionStart, selectionEnd) + '[/' + tagName + ']' + 
            text.substring(selectionEnd, text.length);

        content.val(text);
        
    });
};


jQuery('.pgf-link-load-on-success').live('click', function(e){
    e.preventDefault();

    var el = jQuery(this);
    var href = el.attr('href');
    var dest = el.data('dest');

    pgf.forms.Post({action: href,
                    OnSuccess: function(data){
                        location.href = dest;
                    },
                    OnError: function(data){
                        alert(data.error);
                    }
                   });
});