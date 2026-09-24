from django import forms
from django.core.exceptions import ValidationError

from .catalog import PaymentMethod
from .models import Customer

FORM_CONTROL = "form-control"


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ("name", "address", "email", "phone", "commune", "payment_method")
        widgets = {
            "payment_method": forms.Select(),
        }

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        if company is not None and not self.instance.pk:
            self.instance.company = company
        for field in self.fields.values():
            field.widget.attrs["class"] = FORM_CONTROL

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        queryset = Customer.objects.filter(
            company=self.instance.company,
            email__iexact=email,
        )
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise ValidationError("Ya existe un cliente con este correo en la compañía.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if not phone:
            raise ValidationError("Ingresa un teléfono válido.")
        return phone

    def clean_payment_method(self):
        payment_method = self.cleaned_data["payment_method"]
        if payment_method not in PaymentMethod.values:
            raise ValidationError("Selecciona una forma de pago válida.")
        return payment_method
