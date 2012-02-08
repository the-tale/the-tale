
if (!window.pgf) {
    pgf = {};
}

if (!pgf.forum) {
    pgf.forum = {};
}

pgf.forum.InitPostFields = function() {
    jQuery('.pgf-command').click(function(e){
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
}
