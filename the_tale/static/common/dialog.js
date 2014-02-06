

if (!window.pgf) {
    pgf = {};
}

if (!pgf.ui) {
    pgf.ui = {};
}

if (!pgf.ui.dialog) {
    pgf.ui.dialog = {};
}

pgf.ui.dialog.DIALOG_OPENED = 'pgf-ui-dialog-opened';
pgf.ui.dialog.DIALOG_CLOSED = 'pgf-ui-dialog-closed';

// arguments
// from_selector - jQuery dialog content selector
// from_string - string with html data
// from_url - url for ajax request
pgf.ui.dialog.Create = function(params) {

    if (!params) alert('dialog.Create - params MUST be specified');

    if (!params.fromSelector && !params.fromString && !params.fromUrl) {
        alert('one of the folowing parameters MUST be set: "fromSelector", "fromString", "fromUrl"');
        return;
    }

    var closeOnEscape = 'closeOnEscape' in params ? params.closeOnEscape : true;
    var title = 'title' in params ? params.title : undefined;

    if (params.fromUrl) CreateFromAjax(params.fromUrl);
    else if (params.fromString) CreateFromString(params.fromString);
    else CreateFromSelector(params.fromSelector);

    function CreateFromAjax(url) {
        pgf.ui.dialog.wait('start');
        jQuery.ajax({
            dataType: 'html',
            type: 'get',
            url: url,
            success: function(data, request, status) {
                pgf.ui.dialog.wait('stop',
                                   stopCallback=function(){
                                       CreateFromString(data);
                                   });
            },
            error: function(request, status, error) {
                pgf.ui.dialog.wait('stop',
                                   stopCallback=function(){
                                       pgf.ui.dialog.Error({ message: 'dialog.Create: error while getting: ' + url });
                                   });
            },
            complete: function(request, status) {
            }
        });
    }

    function CreateFromSelector(selector) {
        CreateFromString(jQuery(selector).html());
    }

    function CreateFromString(string) {

        var content = string;

        content = jQuery(content);

        if (title) {
            jQuery('.pgf-dialog-title', content).html(title);
        }

        var dialog = undefined;

        var OnShow = function(e) {
            if (!$(e.target).is(dialog)) return;

            jQuery('.modal').not(dialog).toggleClass('nested-modal', true);

            jQuery('.pgf-close-dialog', dialog).click(function(e){
                e.preventDefault();
                dialog.modal('hide');
            });

            if (params.OnOpen) {
                params.OnOpen(dialog);
            }
        };

        var OnShown = function(e) {
            if (!$(e.target).is(dialog)) return;

            pgf.base.AutoFormatTime();

            if (params.OnOpened) {
                params.OnOpened(dialog);
            }

            dialog.bind('mousewheel', function(e){
                var target = jQuery(e.target);
                if (target.closest('.pgf-scrollable').length == 0) {
                    // if event will not processed by main scroll event processor
                    e.preventDefault();
                }
            });

            jQuery(document).trigger(pgf.ui.dialog.DIALOG_OPENED, dialog);
        };

        var OnHide = function(e) {
            if (!$(e.target).is(dialog)) return;

            jQuery('.modal').not(dialog).toggleClass('nested-modal', false);

            if (params.OnClose) {
                params.OnClose(dialog);
            }

        };

        var OnHidden = function(e) {
            if (!$(e.target).is(dialog)) return;

            if (params.OnClosed) {
                params.OnClosed(dialog);
            }
            jQuery(document).trigger(pgf.ui.dialog.DIALOG_CLOSED, dialog);
            dialog.remove();
        };

        dialog = jQuery(content)
            .modal({keyboard: closeOnEscape, show: false})
            .bind('show', OnShow)
            .bind('shown', OnShown)
            .bind('hide', OnHide)
            .bind('hidden', OnHidden);

        dialog.modal('show');
    }
};

pgf.ui.dialog.Question = function(params) {

    var content = "<div><div class='modal hide'><div class='modal-header'><button type='button' class='close' data-dismiss='modal'>×</button><h3 class='pgf-dialog-title'></h3></div><div class='modal-body'></div><div class='modal-footer'>";

    for (var i in params.buttons) {
        var button = params.buttons[i];
        button.classes = button.classes ? button.classes : '';

        var html = "<a href='#' class='btn pgf-dialog-button-" + i + ' ' + button.classes + "' data-dismiss='modal'>" + button.text + "</a>";

        content += html;
    }

    content += "</div></div></div>";

    var dialog = jQuery(content);

    var title = 'title' in params ? params.title : 'Внимание!';

    if (!params.message) {
        pgf.ui.dialog.Error({message: 'dialog.Question: message does not specified'});
    }

    jQuery('.modal-body', dialog).html(params.message);

    pgf.ui.dialog.Create({fromSelector: dialog,
                          title: title,
                          OnClose: function(dialog) {
                              if (params.OnClose) params.OnClose(dialog);
                          },
                          OnOpen: function(dialog){
                              for (var i in params.buttons) {
                                  var button = params.buttons[i];
                                  if (button.callback) {
                                      jQuery('.pgf-dialog-button-'+i, dialog).click(button.callback);
                                  }
                              }
                          }
                         });
};

pgf.ui.dialog.Alert = function(params) {

    var title = 'title' in params ? params.title : 'Внимание!';

    if (!params.message) {
        pgf.ui.dialog.Error({message: 'dialog.Alert: message does not specified'});
    }

    function OkCallback(e) {
        if (params.OnOk) params.OnOk();
    }

    pgf.ui.dialog.Question({message: params.message,
                            title: title,
                            OnClose: OkCallback,
                            buttons: [{text: 'Ok',
                                       callback: OkCallback}]
                           });

};

pgf.ui.dialog.Error = function(params) {

    params.message = '<div class="alert alert-error">' + params.message + '</div>';

    pgf.ui.dialog.Alert(params);
};


pgf.ui.dialog._wait_counter = 0;
pgf.ui.dialog._wait_content = '<div class="pgf-wait-backdrop modal-backdrop wait-backdrop in" style=";"></div>';
pgf.ui.dialog._wait_indicator_content = '<div class="wait-indicator-backdrop pgf-wait-indicator-backdrop"><div class="pgf-wait-indicator block wait-indicator"></div></div>';
pgf.ui.dialog._WAIT_MINIMUM_LOCK_DELAY = 750;
pgf.ui.dialog._wait_start_time = undefined;
pgf.ui.dialog._wait_close_timer = undefined;
pgf.ui.dialog.closeWait = function() {
    jQuery('.pgf-wait-indicator').spin(false);
    jQuery('.pgf-wait-backdrop').remove();
    jQuery('.pgf-wait-indicator-backdrop').remove();
};
pgf.ui.dialog.wait = function(command, stopCallback) {

    if (!stopCallback) {
        stopCallback = function(){};
    }

    if (command == 'start') {
        pgf.ui.dialog._wait_counter += 1;
        if (pgf.ui.dialog._wait_counter > 1) {
            return;
        }
        jQuery('body').append(pgf.ui.dialog._wait_content).append(pgf.ui.dialog._wait_indicator_content);
        jQuery('.pgf-wait-indicator').spin('large');

        var date = new Date();
        pgf.ui.dialog._wait_start_time = date.getTime();

        if (pgf.ui.dialog._wait_close_timer) {
            clearTimeout(pgf.ui.dialog._wait_close_timer);
        }
    }

    if (command == 'stop') {
        pgf.ui.dialog._wait_counter -= 1;
        if (pgf.ui.dialog._wait_counter > 0) {
            return;
        }

        var date = new Date();
        var curTime = date.getTime();
        var minCloseTime =  pgf.ui.dialog._wait_start_time + pgf.ui.dialog._WAIT_MINIMUM_LOCK_DELAY;

        if ( minCloseTime <= curTime) {
            pgf.ui.dialog.closeWait();
            stopCallback();
        }
        else {
            pgf.ui.dialog._wait_close_timer = window.setTimeout(function() { pgf.ui.dialog.closeWait();
                                                                             stopCallback(); }, minCloseTime - curTime);
        }
    }
};


jQuery('.pgf-dialog-simple').live('click', function(e) {
    e.preventDefault();

    var el = jQuery(this);

    pgf.ui.dialog.Create({ fromUrl: el.attr("href") });
});
