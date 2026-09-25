from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import redirect

from .models import Company


class CompanyRequiredMixin:
    def get_company(self):
        return Company.objects.filter(created_by=self.request.user).first()

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_staff:
            raise PermissionDenied("Un usuario Staff no puede gestionar información de compañía.")
        if self.get_company() is None:
            messages.info(request, "Configura tu compañía para acceder a esta sección.")
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)


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