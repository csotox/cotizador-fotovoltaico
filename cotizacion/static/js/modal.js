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
                initializeStockField();
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

    function showConfirmDialog(message, form) {
        var modalElement = document.createElement("div");
        modalElement.className = "modal fade";
        modalElement.tabIndex = -1;
        modalElement.innerHTML = '<div class="modal-dialog modal-dialog-centered"><div class="modal-content"><div class="modal-header"><h5 class="modal-title">Confirmar acción</h5><button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button></div><div class="modal-body"><p class="mb-0"></p></div><div class="modal-footer"><button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Cancelar</button><button type="button" class="btn btn-danger">Eliminar</button></div></div></div>';
        document.body.appendChild(modalElement);
        modalElement.querySelector(".modal-body p").textContent = message;
        var modal = bootstrap.Modal.getOrCreateInstance(modalElement);
        modalElement.querySelector("[data-bs-dismiss='modal']:not(.btn-close)").addEventListener("click", function () { modal.hide(); });
        modalElement.querySelector(".btn-danger").addEventListener("click", function () { form.submit(); });
        modalElement.addEventListener("hidden.bs.modal", function () { modalElement.remove(); });
        modal.show();
    }

    function setLoading(form) {
        form.querySelectorAll("button[type='submit']").forEach(function (button) {
            button.disabled = true;
            button.dataset.originalText = button.textContent;
            button.textContent = "Guardando...";
        });
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

        function initializeStockField() {
            var $kind = $("#id_kind");
            var $stock = $("#id_stock_quantity");
            if ($kind.length && $stock.length) {
                $stock.prop("disabled", $kind.val() !== "product");
            }
        }

        $(document).on("shown.bs.modal", "#appModal", initializeStockField);

        $(document).on("change", "#id_kind", function () {
            var $kind = $(this);
            var $stock = $("#id_stock_quantity");
            $stock.prop("disabled", $kind.val() !== "product");
            if ($kind.val() !== "product") {
                $stock.val("");
            }
        });

        $(document).on("submit", "form[data-confirm]", function (event) {
            event.preventDefault();
            showConfirmDialog(this.getAttribute("data-confirm"), this);
        });

        $(document).on("submit", "form:not(#appModal form)", function () {
            if (!this.hasAttribute("data-confirm")) {
                setLoading(this);
            }
        });

        $(document).on("submit", BODY_SELECTOR + " form", function (event) {
            event.preventDefault();
            var $form = $(this);
            var $submit = $form.find("button[type='submit']").first();

            var originalText = $submit.text();
            $submit.data("original-text", originalText);
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
                    $submit.text($submit.data("original-text") || originalText);
                    $submit.prop("disabled", false);
                });
        });
    });
})(jQuery);