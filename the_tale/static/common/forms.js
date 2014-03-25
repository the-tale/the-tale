if (!window.pgf) {
    pgf = {};
}

if (!pgf.forms) {
    pgf.forms = {};
}

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

        var instance = this;
    };

    this.ClearErrors = function() {
        var form = jQuery(this.selector);
        jQuery('.pgf-error-container').toggleClass('pgf-hidden', true);
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
                container = jQuery('.pgf-error-container.pgf-form-marker', form).toggleClass('pgf-hidden', false);
            }
            else {
                container = jQuery('.pgf-error-container.pgf-form-field-marker-'+name, form).toggleClass('pgf-hidden', false);
            }

            container.parents().filter('.pgf-widget').toggleClass('error', true);

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
                    instance.DisplayErrors({__all__: ['Произошла ошибка, мы уже работаем над её устранением, повторите попытку через некоторое время']});
                }
            }
        }
        if (data.status == 'processing') {
            pgf.ui.dialog.wait("start");
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
        instance.DisplayErrors({__all__: ['Произошла ошибка, мы уже работаем над её устранением, повторите попытку через некоторое время']});
    }

    function OnComplete(request, status) {
        pgf.ui.dialog.wait("stop");
    }

    this.Submit = function() {
        pgf.ui.dialog.wait("start");
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

    if (!('wait' in params)) params.wait = true;

    if (!('type' in params)) params.type = 'post';

    function OnSuccess(data, request, status) {
        if (data.status == 'ok') {
            if (params.OnSuccess) {
                params.OnSuccess(data);
            }
        }

        if (data.status == 'error') {
            if (data.error) {
                pgf.ui.dialog.Error({message: data.error});
            }
            else {
                if (data.errors && data.errors.length > 0) {
                    pgf.ui.dialog.Error({message: data.errors[0]});
                }
                else {
                    pgf.ui.dialog.Error({message: 'Произошла ошибка, мы уже работаем над её устранением, повторите попытку через некоторое время'});
                }
            }
            if (params.OnError) {
                params.OnError(data);
            }
        }

        if (data.status == 'processing') {
            if (params.wait) {
                pgf.ui.dialog.wait("start");
            }

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
            pgf.ui.dialog.Error({message: 'Произошла ошибка, мы уже работаем над её устранением, повторите попытку через некоторое время'});
        }
    }

    function OnComplete() {
        if (params.wait) {
            pgf.ui.dialog.wait("stop");
        }
        if (params.OnComplete) {
            params.OnComplete();
        }
    }

    if (params.wait) {
        pgf.ui.dialog.wait("start");
    }
    jQuery.ajax({
        dataType: 'json',
        type: params.type,
        url: params.action,
        data: params.data,
        success: OnSuccess,
        error: OnError,
        complete: OnComplete
    });
};


jQuery('.pgf-forms-post-simple').live('click', function(e) {
    e.preventDefault();

    var el = jQuery(this);

    if (el.hasClass('pgf-disabled')) return;

    var actionType = el.data('action-type');

    if (!actionType) actionType = 'reload';

    var url = el.attr('href');

    if (!url) return;

    var confirmation = el.data('confirmation');
    var successMessage = el.data('success-message');
    var successEvent = el.data('success-event');

    function ProcessData(data) {
        if (actionType == 'quietly') {
        }
        if (actionType == 'reload') {
            location.reload(true);
        }
        if (actionType == 'redirect') {
            location.href = el.data('redirect-url');
        }
        if (actionType == 'event') {
            jQuery(document).trigger(successEvent);
        }
    }

    var Operation = function() {
        pgf.forms.Post({ action: url,
                         OnSuccess: function(data){
                             if (data && data.data && data.data.message) {
                                 successMessage = data.data.message;
                             }

                             if (successMessage) {
                                 pgf.ui.dialog.Alert({message: successMessage,
                                                      title: 'Операция завершена',
                                                      OnOk: function(e){ProcessData(data)}});
                                 return;
                             }
                             ProcessData(data);
                         }
                       }); };

    if (confirmation) {
        pgf.ui.dialog.Question({message: confirmation,
                                title: 'Подтвердите операцию',
                                buttons: [{text: 'Подтверждаю', classes: 'btn-success', callback: Operation},
                                          {text: 'Отмена', classes: 'btn-danger'}]
                               });
    }
    else {
        Operation();
    }
});
