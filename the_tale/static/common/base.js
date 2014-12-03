
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


pgf.base.ToggleWait = function(element, wait) {
    element.spin(wait ? 'tiny' : false);
    element.toggleClass('wait', wait).toggleClass('pgf-wait', wait);
};

pgf.base.InitializeTabs = function(settingName, def, tabs) {

    var tabShowed = false;

    for (var i in tabs) {
        var selector = jQuery(tabs[i][0]);

        if (selector.length == 0) {
            continue;
        }

        var id = tabs[i][1];

        if (pgf.base.settings.get(settingName, def) == id) {
            selector.tab('show');
            tabShowed = true;
        }

        (function(id) {
            selector.click(function(e){
                               pgf.base.settings.set(settingName, id);
                           });
        })(id);
    }

    if (!tabShowed) {
        for (var i in tabs) {
            var selector = jQuery(tabs[i][0]);

            if (selector.length) {
                selector.tab('show');
                break;
            }
        }
    }
};

pgf.base.TooltipPlacement = function (tip, element) {
    element = jQuery(element);

    var offset = element.offset();
    var placement = element.data('tooltip-placement');

    if (!placement) {
        var height = jQuery(document).outerHeight();
        var width = jQuery(document).outerWidth();
        var vert = 0.5 * height - offset.top;
        var vertPlacement = vert > 0 ? 'bottom' : 'top';
        var horiz = 0.5 * width - offset.left;
        var horizPlacement = horiz > 0 ? 'right' : 'left';
        placement = Math.abs(horiz) > Math.abs(vert) ?  horizPlacement : vertPlacement;
    }
    return placement;
};

pgf.base.HorizTooltipPlacement = function (tip, element) {
    element = jQuery(element);

    var offset = element.offset();
    var placement = element.data('tooltip-placement');

    if (!placement) {
        var width = jQuery(document).outerWidth();
        var horiz = 0.5 * width - offset.left;
        var horizPlacement = horiz > 0 ? 'right' : 'left';
        placement = horizPlacement;
    }
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

pgf.base._FindParentsForChildren = function(parent, child) {
    if (child) return jQuery('.'+parent+' .'+child).closest('.'+parent);
    return jQuery('.'+parent);
};

pgf.base.HideTooltips = function(clearedContainer, child_class) {
    pgf.base._FindParentsForChildren('popover', child_class).remove();
    pgf.base._FindParentsForChildren('tooltip', child_class).remove();

    if (clearedContainer) {
        // TODO: data('x').enabled = false — totally disabled toltips, we need other way to hide them
        // TODO: is first processing needed????
        jQuery('.pgf-has-popover', clearedContainer).each(function(i, el){
                                                              el = jQuery(el);
                                                              el.data('popover').enabled = false;
                                                          });
        jQuery('[rel="popover"]', clearedContainer).each(function(i, el){
                                                             el = jQuery(el);
                                                             el.data('popover').enabled = false;
                                                         });
        jQuery('[rel="tooltip"]', clearedContainer).each(function(i, el){
                                                             el = jQuery(el);
                                                             el.data('tooltip').enabled = false;
                                                         });
        if (clearedContainer.data('tooltip')) clearedContainer.data('tooltip').enabled = false;
        if (clearedContainer.data('popover')) clearedContainer.data('tooltip').enabled = false;
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
    var date = new Date();

    jQuery('.pgf-format-datetime').each(function(i, v){
        var el = jQuery(v);
        var timestamp = parseInt(el.data('timestamp'), 10) * 1000;
        var text = Globalize.format( new Date(timestamp), "d" ) + ' ' + Globalize.format( new Date(timestamp), "t" );
        el.text(text);
    });

    jQuery('.pgf-format-date').each(function(i, v){
        var el = jQuery(v);
        var timestamp = parseInt(el.data('timestamp'), 10) * 1000;
        var text = Globalize.format( new Date(timestamp), "d" );
        el.text(text);
    });

    jQuery('.pgf-format-time').each(function(i, v){
        var el = jQuery(v);
        var timestamp = parseInt(el.data('timestamp'), 10) * 1000;
        var text = Globalize.format( new Date(timestamp), "t" );
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

        var single = target.data('single');

        if (single) {
            text = text.substring(0, selectionStart) +
                '[' + tagName + ']' + text.substring(selectionStart, selectionEnd) +
                text.substring(selectionEnd, text.length);
        }
        else {
            text = text.substring(0, selectionStart) +
                '[' + tagName + ']' + text.substring(selectionStart, selectionEnd) + '[/' + tagName + ']' +
                text.substring(selectionEnd, text.length);
        }

        content.val(text);

    });
};

pgf.base.CompareObjects = function(a, b)
{
  if (a == undefined && b != undefined) return false;
  if (b == undefined && a != undefined) return false;

  var p;
  for(p in a) {
      if(typeof(b[p])=='undefined') {return false;}
  }

  for(p in a) {
      if (a[p]) {
          switch(typeof(a[p])) {
              case 'object':
                  if (!pgf.base.CompareObjects(a[p],b[p])) { return false; } break;
              case 'function':
                  if (typeof(b[p])=='undefined' ||
                      (a[p].toString() != b[p].toString()))
                      return false;
                  break;
              default:
                  if (a[p] != b[p]) { return false; }
          }
      } else {
          if (b[p])
              return false;
      }
  }

  for(p in b) {
      if(typeof(a[p])=='undefined') {return false;}
  }

  return true;
};


// convert subset of html into bbcode
pgf.base.HTMLToBBcode = function(text) {

    text = text
        .replace(/<strong>/g, '[b]')
        .replace(/<\/strong>/g, '[/b]')

        .replace(/<em>/g, '[i]')
        .replace(/<\/em>/g, '[/i]')

        .replace(/<u>/g, '[u]')
        .replace(/<\/u>/g, '[/u]')

        .replace(/<strike>/g, '[s]')
        .replace(/<\/strike>/g, '[/s]')

        .replace(/<blockquote>/g, '[quote]')
        .replace(/<\/blockquote>/g, '[/quote]')

        .replace(/<ul>/g, '[list]')
        .replace(/<\/ul>/g, '[/list]')

        .replace(/<li>/g, '[*]')
        .replace(/<\/li>/g, '')

        .replace(/<img src="([^"]*)">/g, '[img]$1[/img]')
        .replace(/<\/img>/g, '')

        .replace(/<a href="([^"]*)">/g, '[url=$1]')
        .replace(/<\/a>/g, '[/url]')

        .replace(/\s+/g, ' ')

        .replace(/<br>/g, '\r')
        .replace(/<hr>/g, '[hr]')

        .replace(/<p>/g, '\r\r')
        .replace(/<\/p>/g, '')

        .replace(/&nbsp;/g, ' ');

    text = text
        .replace(/<[^>]*>/g, "")
        .replace(/&lt;/g, '<')
        .replace(/&gt;/g, '>');

    return text;
};


pgf.base.OpenFancybox = function(images) {
          jQuery.fancybox.open(images, {  padding: 0,
                                          nextClick: true,
                                          openEffect: "fade",
                                          closeEffect: "fade",
                                          nextEffect: "fade",
                                          prevEffect: "fade",
                                          openSpeed: 500,
                                          closeSpeed: 500,
                                          nextSpeed: 500,
                                          prevSpeed: 500});
};

pgf.base.OpenFancyboxIntroComix = function(staticContent) {
    var images = [];

    if (staticContent.indexOf('http:') == -1) {
        staticContent = 'http:'+staticContent;
    }

    for (var i=0; i < 24; ++i) {
        var name = i < 10 ? '0'+i : i;
        images.push({href : staticContent + "images/intro_comix/"+name+".gif"});
    }

    pgf.base.OpenFancybox(images);
};
