
if (!window.pgf) {
    pgf = {};
}

if (!pgf.base) {
    pgf.base = {};
}

pgf.base.tooltipsArgs = { animation: true,
                          placement: 'left',
                          delay: { show: 500,
                                   hidr: 100 } };

pgf.base.RenderTemplateList = function(selector, data, newElementCallback, params) {
    
    var container = jQuery(selector);
    var template = jQuery('.pgf-template', container).eq(0);
    var emptyTemplate = jQuery('.pgf-empty-template', container).eq(0);

    // pgf.tooltips.Hide(container);

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

    // pgf.tooltips.Refresh(container);

};

pgf.base.AutoFormatTime = function() {
    jQuery('.pgf-format-time').each(function(i, v){
        var el = jQuery(v);
        var timestamp = parseInt(el.data('timestamp'), 10) * 1000;
        var text = Globalize.format( new Date(timestamp), "d" ) + ' ' + Globalize.format( new Date(timestamp), "t" ) + ' UTC';
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
        editButton.toggleClass('pgf-hidden', !preview)
        previewContent.toggleClass('pgf-hidden', !preview)
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
}

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