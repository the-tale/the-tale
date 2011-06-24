
jQuery(document).ajaxError( function(event, xhr, ajaxSettings, thrownError) {
    
    var error_wnd =  window.open('','errpr');
    var html = xhr.responseText;
    error_wnd.document.open();
    error_wnd.document.write(html);
    error_wnd.document.close();
});