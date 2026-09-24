(function ($) {
    "use strict";

    var MODAL_SELECTOR = "#appModal";
    var TITLE_SELECTOR = "#appModalLabel";
    var BODY_SELECTOR = "#appModalBody";
    var TRIGGER_SELECTOR = "[data-modal-open]";

    function getModal() {
        var el = document.querySelector(MODAL_SELECTOR);
        return bootstrap.Modal.getOrCreateInstance(el);
    }

    function setTitle(title) {
        $(TITLE_SELECTOR).text(title || "");
    }

    function setBody(html) {
        $(BODY_SELECTOR).html(html);
    }

    function loadingMessage() {
        return '<p class="text-muted mb-0">Cargando...</p>';
    }

    function openModal(url, title) {
        setTitle(title);
        setBody(loadingMessage());
        getModal().show();
        $.get(url)
            .done(function (html) {
                setBody(html);
            })
            .fail(function () {
                setBody(
                    '<div class="alert alert-danger mb-0">No se pudo cargar el formulario.</div>'
                );
            });
    }

    function isSuccessResponse(response) {
        try {
            var data = JSON.parse(response);
            return data && data.success === true;
        } catch (e) {
            return false;
        }
    }

    $(document).ready(function () {
        $(document).on("click", TRIGGER_SELECTOR, function (event) {
            event.preventDefault();
            var $trigger = $(this);
            openModal(
                $trigger.data("modal-open"),
                $trigger.data("modal-title")
            );
        });

        $(document).on("submit", BODY_SELECTOR + " form", function (event) {
            event.preventDefault();
            var $form = $(this);
            var $submit = $form.find("button[type='submit']").first();

            $submit.prop("disabled", true);

            $.ajax({
                url: $form.attr("action"),
                method: "POST",
                dataType: "text",
                data: $form.serialize() + "&form=modal",
            })
                .done(function (response) {
                    if (isSuccessResponse(response)) {
                        getModal().hide();
                        window.location.reload();
                    } else {
                        setBody(response);
                    }
                })
                .fail(function () {
                    setBody(
                        '<div class="alert alert-danger mb-0">No se pudo guardar. Intenta nuevamente.</div>'
                    );
                })
                .always(function () {
                    $submit.prop("disabled", false);
                });
        });
    });
})(jQuery);