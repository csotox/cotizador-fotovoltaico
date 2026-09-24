from django.http import JsonResponse


class ModalFormMixin:
    MODAL_PARAM = "form"

    def is_modal(self):
        return (
            self.request.GET.get(self.MODAL_PARAM) == "modal"
            or self.request.POST.get(self.MODAL_PARAM) == "modal"
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.is_modal():
            return JsonResponse({"success": True})
        return response

    def form_invalid(self, form):
        if self.is_modal():
            return self.render_to_response(self.get_context_data(form=form))
        return super().form_invalid(form)