
jQuery(document).ajaxError( function(event, xhr, ajaxSettings, thrownError) {
    
    var error_wnd =  window.open('','error');
    var text = xhr.responseText;
    error_wnd.document.open();
    error_wnd.document.write('<html><body><pre>' + text + '</pre></body></html>');
    error_wnd.document.close();
});