

if (!window.pgf) {
    pgf = {};
}

if (!pgf.ui) {
    pgf.ui = {};
}

if (!pgf.ui.dialog) {
    pgf.ui.dialog = {};
}

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
        jQuery.ajax({
            dataType: 'html', 
            type: 'get',
            url: url,
            success: function(data, request, status) {
                CreateFromString(data);
            },
            error: function(request, status, error) {
                pgf.ui.dialog.Error({ message: 'dialog.Create: error while getting: ' + url });
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

        dialog = jQuery(content).modal({   keyboard: closeOnEscape,
                                           show: true,
                                           hide: function() {
                                               if (params.OnClose) {
                                                   params.OnClose(dialog);
                                               }

                                               dialog.dialog('destroy');
                                           },
                                           show: function() {
                                               if (params.OnOpen) {
                                                   params.OnOpen(dialog);
                                               }
                                           }
                                       });

    }
};

pgf.ui.dialog.Alert = function(params) {

    var content = "<div><div class='modal hide'><div class='modal-header'><button type='button' class='close' data-dismiss='modal'>×</button><h3 class='pgf-dialog-title'></h3></div><div class='modal-body'></div><div class='modal-footer'><a href='#' class='btn' data-dismiss='modal'>Ok</a></div></div></div>";

    var dialog = jQuery(content);

    var title = 'title' in params ? params.title : 'Внимание!';

    if (!params.message) {
        pgf.ui.dialog.Error({message: 'dialog.Alert: mesage does not specified'});
    }
    
    jQuery('.modal-body', dialog).html(params.message);

    // dialog.modal({});
    pgf.ui.dialog.Create({fromSelector: dialog,
                          title: title});
};

pgf.ui.dialog.Error = function(params) {
    pgf.ui.dialog.Alert(params);
}


pgf.ui.dialog._wait_counter = 0;
pgf.ui.dialog._wait_dialog = undefined;
pgf.ui.dialog.wait = function(command) {

    if (pgf.ui.dialog._wait_dialog == undefined) {
        html = '<div><img src="'+STATIC_URL+'images/waiting.gif"></img></div>';
        pgf.ui.dialog._wait_dialog = jQuery(html).dialog({ autoOpen: false, 
                                                           closeOnEscape: false,
                                                           draggable: false,
                                                           modal: true,
                                                           resizable: false,
                                                           width: 'auto',
                                                           height: 'auto',
                                                           dialogClass: 'waiting-dialog',
                                                           minHeight: 0
                                                         });
    }

    if (command == 'start') {
        pgf.ui.dialog._wait_counter += 1;
        if (pgf.ui.dialog._wait_counter > 1) {
            return;
        }
        pgf.ui.dialog._wait_dialog.dialog("open");
    }

    if (command == 'stop') {
        pgf.ui.dialog._wait_counter -= 1;
        if (pgf.ui.dialog._wait_counter > 0) {
            return;
        }
        pgf.ui.dialog._wait_dialog.dialog("close");
    }

   
};