

if (!window.pgf) {
    pgf = {};
}

if (!pgf.ui) {
    pgf.ui = {};
}

pgf.ui.Dialog = function(params) {

    this.Init = function(){
    };
    
    this.Open = function() {

        if (params.url){
            this.OpenUrl();
        }
    };

    this.OpenUrl = function() {

        var instance = this;
        
        jQuery.ajax({
            // dataType: 'text/html', TODO: set mime time on the server side
            type: 'get',
            url: instance.params.url,
            success: function(data, request, status) {

                var scripts = jQuery(data).filter('script');
                var content = jQuery('<div></div>').append(jQuery(data).not('script'));

                var OnClose = function(e, ui) {
                    $(this).dialog('destroy');
                    $(this).remove();
                    scripts.remove();

                    if (params.OnClose) {
                        params.OnClose( jQuery(e.target) );
                    }
                };
                
                var OnOpen = function(e, ui) {
                    if (params.OnOpen) {
                        params.OnOpen( jQuery(e.target) );
                    }
                };

                scripts.appendTo('body');

                jQuery(content).dialog({ 
                    closeOnEscape: true,
                    minWidth: 400,
                    modal: true,
                    width: 'auto',
                    close: OnClose,
                    open: OnOpen
                });
            },
            error: function(request, status, error) {
                alert('Error while getting: ' + instance.params.url);
            },
            complete: function(request, status) {
            }
        });
    };

    this.Alert = function() {
    };

    this.params = jQuery.extend(true, {}, params);
    this.Init();    
};

pgf.ui.Alert = function(params) {

    var content = "" +
        "<div>"+
        "<h2>"+params.message+"<h2>"
        "</div>";

    jQuery(content).dialog({ 
        closeOnEscape: true,
        minWidth: 400,
        modal: true,
        width: 500,
        close: function(event, ui){
            if (params.OnClose) {
                params.OnClose();
            }
        }
    });
};