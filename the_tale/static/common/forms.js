if (!window.pgf) {
    pgf = {};
}

if (!pgf.forms) {
    pgf.forms = {};
}

// owner - dom element
// form - pgf.form object
pgf.widgets = {

    'static-value': function(name, widget, owner, form) {
        
        var value = jQuery('.pgf-value', widget);

        var displayedValue = jQuery('.pgf-displayed-value', widget);

        this.value = function() {
            return value.val();
        };

        this.set = function(newVal) {
            displayedValue.text(newVal);
            value.val(newVal);
        };
    },

    'integer-interval': function(name, widget, owner, form) {
        var plus = jQuery('.pgf-plus', widget);
        var minus = jQuery('.pgf-minus', widget);
        var value = jQuery('.pgf-value', widget);

        var interval = {min: parseInt(widget.data('interval-min')),
                        max: parseInt(widget.data('interval-max')) };

        var limitedByWidget = widget.data('limited-by');

        var instance = this;

        function CreateBtnCallback(delta) {
            return function(e){
                e.preventDefault();
                if (form && form.widgets && limitedByWidget in form.widgets) {
                    var limit = form.widgets[limitedByWidget];
                    var free = parseInt(limit.value());

                    if (free - delta < 0) return;

                    if (instance.change(delta)) {
                        limit.set(free - delta);
                    }
                    return;
                }
                instance.change(delta);
            }
        }

        plus.click( CreateBtnCallback(1) );
        minus.click( CreateBtnCallback(-1) );

        this.change = function(delta) {
            var val = parseInt(value.val());
            var newVal = val + delta;

            if (interval.min <= newVal && newVal <= interval.max) {
                value.val(newVal);
                return true;
            }
            return false;
        };
    }
};

pgf.forms.Form = function(selector, params) {

    var instance = this;

    this.Init = function(selector, params) {

        this.selector = selector;
        this.defaults = {};

        this.params = jQuery.extend({}, 
                                    this.defaults,
                                    params);

        var form = jQuery(selector);
        
        this.ClearErrors();

        form.submit(function(e){
            e.preventDefault();
            instance.Submit();
        });

        if (this.params.action === undefined) {
            this.params.action = form.attr('action');
        }

        this.widgets = {};

        var instance = this;

        jQuery('.pgf-widget', form).each( function(i, v) {
            el = jQuery(v);
            var widgetName = el.data('widget-name');
            var widgetType = el.data('widget-type');

            if (widgetType in pgf.widgets) {
                instance.widgets[widgetName] = new pgf.widgets[widgetType](widgetName, el, form, instance);
            }
        });
    };

    this.ClearErrors = function() {
        var form = jQuery(this.selector);
        jQuery('.pgf-form-errors', form).html('');
        jQuery('.pgf-form-field-errors', form).html('');
        jQuery('.pgf-widget', form).toggleClass('error', false);
    };

    this.DisplayErrors = function(errors) {
        var form = jQuery(this.selector);

        jQuery('.pgf-error-container', form).html('');

        for (var name in errors) {
            var container = undefined;
            if (name == '__all__') {
                container = jQuery('.pgf-error-container.pgf-form-marker', form);
            }
            else {
                container = jQuery('.pgf-error-container.pgf-form-field-marker-'+name, form);
            }

            jQuery('.pgf-widget', container.parents()).toggleClass('error', true);

            var errors_list = errors[name];
            container.html('');
            for (var j in errors_list) {
                var error_content = '<div class="pgf-error-text error-text">'+errors_list[j]+'</div>';
                container.append(error_content);
            }
        }
    };

    function OnSuccess(data, request, status) {
        instance.ClearErrors();
        if (data.status === 'ok') {
            if (instance.params.OnSuccess) {
                instance.params.OnSuccess(instance, data);
            }
        }
        if (data.status == 'error') {
            if (data.error) {
                instance.DisplayErrors({__all__: [data.error]});
            }
            else {
                if (data.errors) {
                    instance.DisplayErrors(data.errors);
                }
                else {
                    instance.DisplayErrors({__all__: ['uncknown error']});
                }
            }
        }
        if (data.status == 'processing') {
            setTimeout(function() {
                jQuery.ajax({dataType: 'json',
                             type: 'get',
                             url: data.status_url,
                             success: OnSuccess,
                             error: OnError,
                             complete: OnComplete});
            }, 1000);
        }
    }

    function OnError(request, status, error) {
        instance.ClearErrors();
        instance.DisplayErrors({__all__: ['uncknown error']});
    }

    function OnComplete(request, status) {
    }

    this.Submit = function() {
        var instance = this;
        jQuery.ajax({
            dataType: 'json',
            type: 'post',
            url: instance.params.action,
            data: jQuery(this.selector).serialize(), 
            success: OnSuccess,
            error: OnError,
            complete: OnComplete
        });
    };

    this.Init(selector, params);
};

pgf.forms.Post = function(params) {

    if (params.confirm && !confirm(params.confirm)) {
        return;
    }

    function OnSuccess(data, request, status) {
        if (data.status == 'ok') {
            if (params.OnSuccess) {
                params.OnSuccess(data);
            }
        }

        if (data.status == 'error') {
            if (data.error) {
                alert(data.error);
            }
            else {
                if (data.errors && data.errors.length > 0) {
                    alert(data.errors[0]);
                }
                else {
                    alert('unknown error occured!');
                }
            } 
            if (params.OnError) {
                params.OnError(data);
            }
        }

        if (data.status == 'processing') {
            setTimeout(function() {
                jQuery.ajax({dataType: 'json',
                             type: 'get',
                             url: data.status_url,
                             success: OnSuccess,
                             error: OnError,
                             complete: OnComplete});
            }, 1000);
        }
    }

    function OnError(data, request, status) {
        if (params.OnError) {
            params.OnError(data);
        }
        else {
            alert('unknown error occured!');
        }
    }

    function OnComplete() {
    }

    jQuery.ajax({
        dataType: 'json',
        type: 'post',
        url: params.action,
        data: params.data,
        success: OnSuccess,
        error: OnError,
        complete: OnComplete
    });
};

pgf.forms.PostSimple = function(url) {
    jQuery.ajax({
        url: url,
        type: 'post',
        dataType: 'json',
        error: function(data) {
            pgf.ui.Alert({message: "unknown error",
                          OnConfirm: function(){location.reload();}
                         });
        },
        success: function(data) {
            if (data) {
                if (data.status === 'error') {
                    if (data.error) {
                        pgf.ui.Alert({message: "Error occured:\n" + data.error,
                                      OnClose: function(){location.reload();}
                                     });
                        return;
                    }
                    if (data.errors) {
                        pgf.ui.Alert({message: "Errors occured:\n" + data.errors,
                                      OnClose: function(){location.reload();}
                                     });
                        return;
                    }
                }
                else {
                    location.reload();
                }
            }
            else {
                location.reload();
            }
        }
    });
};

jQuery('.pgf-forms-post-simple').live('click', function(e) {
    e.preventDefault();

    var el = jQuery(this);

    if (el.attr('href')) {
        pgf.forms.PostSimple(el.attr('href'));
    }
});

